#!/usr/bin/env python3
"""Data preparation for CECP CoP21 website.

1. Requires the following eight C-REM model runs. As of 2016-04-24, separate
   commits of C-REM must be used to run the base and 'less-GDP' cases; see
   https://github.com/mit-jp/crem/issues/35.

# Base cases
crem gdx/result_urban_exo -- --case=default
crem gdx/result_cint_n_3 -- --case=cint_n --cint_n_rate=3
crem gdx/result_cint_n_4 -- --case=cint_n --cint_n_rate=4
crem gdx/result_cint_n_5 -- --case=cint_n --cint_n_rate=5

# Low-growth cases
crem gdx/result_urban_exo_lessGDP -- --case=default
crem gdx/result_cint_n_3_lessGDP -- --case=cint_n --cint_n_rate=3
crem gdx/result_cint_n_4_lessGDP -- --case=cint_n --cint_n_rate=4
crem gdx/result_cint_n_5_lessGDP -- --case=cint_n --cint_n_rate=5')

"""
import csv
from collections import OrderedDict
from pathlib import Path
from subprocess import run

import gdx
from numpy import nan
from openpyxl import load_workbook
import pandas as pd
import xarray as xr

# File locations
GDX_DIR = Path('.', 'gdx')
OUT_DIR = Path('..', '..', '..', 'cecp-cop21-data')

# (label, filename, description) for each scenario
CASE_INFO = [
    ('bau', 'result_urban_exo',
     'BAU: Business-as-usual'),
    ('3', 'result_cint_n_3',
     'Policy: Reduce carbon-intensity of GDP by 3%/year from BAU'),
    ('4', 'result_cint_n_4',
     'Policy: Reduce carbon-intensity of GDP by 4%/year from BAU'),
    ('5', 'result_cint_n_5',
     'Policy: Reduce carbon-intensity of GDP by 5%/year from BAU'),
    # 2018-04-21 pnk: final version of site does not use these data
    ('bau_lo', 'result_urban_exo_lessGDP',
     'LO: BAU with 1% lower annual GDP growth'),
    ('3_lo', 'result_cint_n_3_lessGDP',
     'Policy: Reduce carbon-intensity of GDP by 3%/year from LO'),
    ('4_lo', 'result_cint_n_4_lessGDP',
     'Policy: Reduce carbon-intensity of GDP by 4%/year from LO'),
    ('5_lo', 'result_cint_n_5_lessGDP',
     'Policy: Reduce carbon-intensity of GDP by 5%/year from LO'),
    ]

PM_FILE = GDX_DIR / 'pm.xlsx'

PM_FILE_FORMAT = 2  # either 1 (ca. 2015) or 2 (ca. 2018)

# 2. Preprocess the GDX files.
#    Some of the quantities used below are stored in the GAMS parameters
#    `report(*,*,*)` and `egyreport2(*,*,*,*)`, which pyGDX cannot handle. The
#    cell below runs the simple GAMS script `pre.gms` to produce a new file
#    named `*foo*_extra.gdx` with the pyGDX-friendly variables `ptcarb_t(t)`,
#    `pe_t(e,r,t)` and `cons_t(r,t)`.
# 3. Read the GDX files
raw = OrderedDict()
extra = dict()
for case, fn, label in CASE_INFO:
    print(case, '--', label)

    # Preprocess
    fn = GDX_DIR / fn
    run(['gams', 'pre.gms', '--file={}'.format(fn)])

    # Read the GDX files
    fn = fn.with_suffix('.gdx')
    try:
        raw[case] = gdx.File(fn)
        extra[case] = gdx.File(str(fn).replace('.gdx', '_extra.gdx'))
    except FileNotFoundError:
        continue

# Use the BAU file to reference dimensions, sets etc.
CREM = raw['bau']

# Indices for result objects
cases = pd.Index(raw.keys(), name='case')
time = pd.Index(filter(lambda t: int(t) <= 2030, CREM.set('t')))

# Description of the scenarios being loaded
scenarios_desc = pd.Series({case[0]: case[2] for case in CASE_INFO})[cases]

# for debugging:
# # List all the parameters available in each file
# CREM.parameters()

# Temporary container for read-in data
arrays = {}


def label(variable, desc, unit_long, unit_short):
    """Add some descriptive attributes to an xr.DataArray."""
    arrays[variable].attrs.update({'desc': desc, 'unit_long': unit_long,
                                   'unit_short': unit_short})


# GDP
temp = [raw[case].extract('gdp_ref') for case in cases]
arrays['GDP'] = xr.concat(temp, dim=cases).sel(rs=CREM.set('r')) \
                    .rename({'rs': 'r'})
label('GDP', 'Gross domestic product',
      'billions of U.S. dollars, constant at 2007', '10⁹ USD')

arrays['GDP_aagr'] = ((arrays['GDP'][:, :, 1:].values /
                       arrays['GDP'][:, :, :-1])
                      ** (1 / CREM.extract('lp')) - 1) * 100
label('GDP_aagr', 'Gross domestic product, average annual growth rate',
      'percent', '%')

arrays['GDP_delta'] = (arrays['GDP'] / arrays['GDP'].sel(case='bau') - 1) * 100
label('GDP_delta', 'Change in gross domestic product relative to BAU',
      'percent', '%')

# CO₂ emissions
temp = []
for case in cases:
    temp.append(raw[case].extract('sectem').sum('g') +
                raw[case].extract('houem'))
arrays['CO2_emi'] = xr.concat(temp, dim=cases)
label('CO2_emi', 'Annual CO₂ emissions',
      'millions of tonnes of CO₂', 'Mt')


# Air pollutant emissions
temp = []
for case in cases:
    # Sum over sectors (unlabelled dimension 2)
    temp.append(raw[case].extract('urban').sum('_urban_2'))

temp = xr.concat(temp, dim=cases) \
         .sel(rs=CREM.set('r')) \
         .rename({'rs': 'r'})

for u in temp['urb']:
    if u in ['PM10', 'PM25']:
        continue
    var_name = '{}_emi'.format(u.values)
    arrays[var_name] = temp.sel(urb=u).drop('urb')
    u_fancy = str(u.values).translate({'2': '₂', '3': '₃'})
    label(var_name, 'Annual {} emissions'.format(u_fancy),
          'millions of tonnes of ' + str(u_fancy), 'Mt')


# CO₂ price
temp = []
for case in cases:
    temp.append(extra[case].extract('ptcarb_t'))
arrays['CO2_price'] = xr.concat(temp, dim=cases)
label('CO2_price', 'Price of CO₂ emissions permit',
      '2007 US dollars per tonne CO₂', '2007 USD/t')


# Consumption
temp = []
for case in cases:
    temp.append(extra[case].extract('cons_t'))
arrays['cons'] = xr.concat(temp, dim=cases)
label('cons', 'Household consumption',
      'billions of U.S. dollars, constant at 2007', '10⁹ USD')


# Primary energy
temp = []
for case in cases:
    temp.append(extra[case].extract('pe_t'))
temp = xr.concat(temp, dim=cases)
temp = temp.where(temp < 1e300).fillna(0)
e_name = {
    'COL': 'Coal',
    'GAS': 'Natural gas',
    'OIL': 'Crude oil',
    'NUC': 'Nuclear',
    'WND': 'Wind',
    'SOL': 'Solar',
    'HYD': 'Hydroelectricity',
    }
for ener in temp['e']:
    var_name = '{}_energy'.format(ener.values)
    # Convert non-fossil electrical energy to the raw quantity of coal needed
    # to generate such amount of electricity:
    arrays[var_name] = temp.sel(e=ener).drop('e') * (1. if ener in
                                                     ['COL', 'GAS', 'OIL'] else
                                                     0.356 / 0.12)
    label(var_name, 'Primary energy from {}'.format(e_name[str(ener.values)]),
          'millions of tonnes of coal equivalent', 'Mtce')

# Sums and shares
arrays['energy_fossil'] = temp.sel(e=['COL', 'GAS', 'OIL']).sum('e')
label('energy_fossil', 'Primary energy from fossil fuels',
      'millions of tonnes of coal equivalent', 'Mtce')

arrays['energy_nonfossil'] = (temp.sel(e=['NUC', 'WND', 'SOL', 'HYD']).sum('e')
                              * 0.356 / 0.12)
label('energy_nonfossil', 'Primary energy from non-fossil sources',
      'millions of tonnes of coal equivalent', 'Mtce')

arrays['energy_total'] = arrays['energy_fossil'] + arrays['energy_nonfossil']
label('energy_total', 'Primary energy, total',
      'millions of tonnes of coal equivalent', 'Mtce')

arrays['penergy_nonfossil_share'] = (arrays['energy_nonfossil'] /
                                     arrays['energy_total']) * 100
label('penergy_nonfossil_share',
      'Share of non-fossil sources in final energy',
      'percent', '%')


# Reported share of NHW
temp1 = []
temp2 = []
for case in cases:
    temp1.append(extra[case].extract('nhw_share'))
    temp2.append(extra[case].extract('nhw_share_CN'))
arrays['energy_nonfossil_share'] = 100 * xr.concat(temp1, dim=cases)
label('energy_nonfossil_share',
      'Share of non-fossil sources in final energy',
      'percent', '%')
nhw_share = 100 * xr.concat(temp2, dim=cases)


# Population
temp = []
for case in cases:
    temp.append(raw[case].extract('pop2007').sel(g='c') *
                raw[case].extract('pop') * 1e-2)
arrays['pop'] = xr.concat(temp, dim=cases).drop('g').sel(rs=CREM.set('r')) \
                    .rename({'rs': 'r'})
label('pop', 'Population', 'millions', '10⁶')


# Share of coal in provincial GDP
temp = []
for case in cases:
    temp.append(raw['bau'].extract('sect_prod'))
sect_prod = xr.concat(temp, dim=cases).sel(rs=CREM.set('r'), g='COL') \
                .drop('g').rename({'rs': 'r'})
arrays['COL_share'] = (sect_prod / arrays['GDP']) * 100
label('COL_share', 'Share of coal production in provincial GDP',
      'percent', '%')


# 3.1. PM2.5 concentrations & population-weighted exposure
#      These are read from a separate XLSX file.

# Open the workbook and worksheet
wb = load_workbook(PM_FILE, read_only=True)

# Mapping from values in the first row of the worksheet(s) to pd.MultiIndex
# labels
cols = {
    None: ('r', ''),
    2010: ('bau', '2010'),
    }
cols.update({
    '2030_BAU': ('bau', '2030'),
    '2030_cint3': ('3', '2030'),
    '2030_cint4': ('4', '2030'),
    '2030_cint5': ('5', '2030'),
    '2030_BAU_lessGDP': ('bau_lo', '2030'),
    '2030_cint3_lessGDP': ('3_lo', '2030'),
    '2030_cint4_lessGDP': ('4_lo', '2030'),
    '2030_cint5_lessGDP': ('5_lo', '2030'),
    } if PM_FILE_FORMAT == 1 else {
    'bau': ('bau', '2030'),
    'cint3': ('3', '2030'),
    'cint4': ('4', '2030'),
    'cint5': ('5', '2030'),
    })

# Storage for extra, ad-hoc values (ie. national-level values)
arrays_extra = {}
for ws in wb:
    # Read the table in to a list of lists
    temp = []
    for r, row in enumerate(ws.rows):
        if r == 0:
            # Construct a 2-level column index from the first row. Put 'drop'
            # on the first level for unrecognized values.
            columns = pd.MultiIndex.from_tuples(
                [cols.get(cell.value, ('drop', cell.value)) for cell in row],
                names=['case', 't'])
        else:
            # Store data
            temp.append([cell.value for cell in row])

    # Convert to a pandas.Series
    df = pd.DataFrame(temp, columns=columns) \
           .dropna(axis=(0, 1), how='all') \
           .set_index([('r', '')]) \
           .drop(columns='drop', errors='ignore') \
           .stack(['case', 't'])
    df.index = df.index.rename(['r', 'case', 't']) \
                       .swaplevel('case', 'r') \
                       .remove_unused_levels()

    # Convert to an xr.DataArray
    da = xr.DataArray.from_series(df)
    # Fill in 2010 values across cases
    da.loc[:, :, '2010'] = da.loc['bau', :, '2010']

    if PM_FILE_FORMAT == 1:
        if ws.title == 'prv_actual_average':
            arrays['PM25_conc'] = da
            label('PM25_conc', 'Province-wide average PM2.5',
                  'micrograms per cubic metre', 'μg/m³')
        elif ws.title == 'prv_pop_average':
            arrays['PM25_exposure'] = da
            label('PM25_exposure', 'Population-weighted exposure to PM2.5',
                  'micrograms per cubic metre', 'μg/m³')
        elif ws.title == 'region_actual_average':
            arrays_extra['PM25_conc'] = da.sel(r='Whole China', drop=True)
        elif ws.title == 'region_pop_average':
            arrays_extra['PM25_exposure'] = da.sel(r='Whole China', drop=True)
    elif PM_FILE_FORMAT == 2:
        # Split off the national data
        da_national = da.sel(r='National', drop=True)
        da = da.where(da.r != 'National', drop=True)

        arrays['PM25_exposure'] = da
        label('PM25_exposure', 'Population-weighted exposure to PM2.5',
              'micrograms per cubic metre', 'μg/m³')

        arrays_extra['PM25_exposure'] = da_national


# Commented: unused on the final website
#
# # Exposed fraction of population
# df = pd.DataFrame([
#     ['bau', '2010', 66.37],
#     ['bau', '2030', 84.78],
#     ['3',   '2030', 78.64],
#     ['4',   '2030', 71.23],
#     ['5',   '2030', 60.87]],
#     columns=['case', 't', 'value']).set_index(['case', 't'])
# da = xr.DataArray.from_series(df['value'])
# # Fill in 2010 values across cases
# da.loc[:, '2010'] = da.loc['bau', '2010']
# arrays_extra['PM25_exposed_frac'] = da
#
# # Placeholder value at regional level
# arrays['PM25_exposed_frac'] = xr.DataArray([nan] * len(time),
#                                            coords=[time],
#                                            dims='t')
# label('PM25_exposed_frac', 'Population exposed to PM2.5 concentrations '
#       'greater than 35 μg/m³', 'percent', '%')


# 3.2. Finish preprocessing

# Combine all variables into a single xr.Dataset and truncate time
data = xr.Dataset(arrays).sel(t=time)

# Description of scenarios
data['scenarios'] = xr.DataArray(scenarios_desc,
                                 coords={'case': cases},
                                 dims='case')

# Commented: unused on the final website
#
# # Interpolate data for missing years.
# for var in [data.PM25_exposure, data.PM25_conc]:
#     # interpolate PM data for missing years
#     var.loc[:,:,'2007'] = var.loc[:,:,'2010']
#     increment = (var.loc[:,:,'2030'] - var.loc[:,:,'2010']) / 4
#     var.loc[:,:,'2015'] = var.loc[:,:,'2010'] + increment
#     var.loc[:,:,'2020'] = var.loc[:,:,'2010'] + 2 * increment
#     var.loc[:,:,'2025'] = var.loc[:,:,'2010'] + 3 * increment
#
# # Construct data for low-ammonia cases
# base_cases = [str(name.values) for name in data['case']]
# nh3_cases = [name + '_nh3' for name in base_cases]
# d = xr.Dataset(coords={'case': nh3_cases})
# data.merge(d, join='outer', inplace=True)
# # fill in PM data for missing cases
# for nh3_case, base_case in zip(nh3_cases, base_cases):
#     data['PM25_conc'].loc[nh3_case, :, :] = data['PM25_conc'] \
#                                             .loc[base_case, :, :]

# Compute national totals and averages
national = data.sum('r')
national['penergy_nonfossil_share'] = (national['energy_nonfossil'] /
                                       national['energy_total']) * 100
national['energy_nonfossil_share'] = nhw_share
national['PM25_exposure'] = arrays_extra['PM25_exposure']

interpolate = ['PM25_exposure']

if PM_FILE_FORMAT == 1:
    national['PM25_exposed_frac'] = arrays_extra['PM25_exposed_frac']
    national['PM25_conc'] = arrays_extra['PM23_conc']
    interpolate.append('PM25_conc')

# Interpolate PM data for missing years
for var in national[interpolate].data_vars.values():
    var.loc[:, '2007'] = var.loc[:, '2010']
    increment = (var.loc[:, '2030'] - var.loc[:, '2010']) / 4
    var.loc[:, '2015'] = var.loc[:, '2010'] + increment
    var.loc[:, '2020'] = var.loc[:, '2010'] + 2 * increment
    var.loc[:, '2025'] = var.loc[:, '2010'] + 3 * increment


# 4. Output data

# Output a file with scenario information
data['scenarios'].to_dataframe() \
                 .sort_index() \
                 .to_csv(OUT_DIR / 'scenarios.csv',
                         header=['description'],
                         quoting=csv.QUOTE_ALL)

# Output a file with variable information
var_info = pd.DataFrame(index=[d for d in data.data_vars if d != 'scenarios'],
                        columns=['desc', 'unit_long', 'unit_short'],
                        dtype=str)

print('Missing dimension info:')
none_missing = True
for name, _ in var_info.iterrows():
    try:
        row = [data[name].attrs[k] for k in var_info.columns]
    except KeyError:
        print('  ', name)
        none_missing = False
        continue
    var_info.loc[name, :] = row
if none_missing:
    print('  (None)')
var_info.sort_index() \
        .to_csv(OUT_DIR / 'variables.csv',
                index_label='Variable',
                quoting=csv.QUOTE_ALL)

# Serialize to CSV
for c in map(lambda x: x.values, data.case):
    # Provincial data
    for r in CREM.set('r'):
        filename = OUT_DIR / r / '{}.csv'.format(c)
        # Create the directory if needed
        filename.parent.mkdir(parents=True, exist_ok=True)
        data.sel(case=c, r=r) \
            .drop(['case', 'r', 'scenarios']) \
            .to_dataframe() \
            .sort_index(axis=1) \
            .to_csv(filename)

    # National data
    filename = OUT_DIR / 'national' / '{}.csv'.format(c)
    filename.parent.mkdir(parents=True, exist_ok=True)
    national.sel(case=c) \
            .drop(['case', 'scenarios']) \
            .to_dataframe() \
            .sort_index(axis=1) \
            .to_csv(filename)
