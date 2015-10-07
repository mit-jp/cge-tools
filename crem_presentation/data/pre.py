
# coding: utf-8

# In[15]:

# Load all the GDX files
import csv
from collections import OrderedDict
from os import makedirs as mkdir
from os.path import join

import gdx
import pandas as pd
import xray

GDX_DIR = 'gdx'
OUT_DIR = '../../../cecp-cop21-data'
FILES = [
    ('bau', 'result_urban_exo.gdx'),
    ('3', 'result_cint_n_3.gdx'),
    ('4', 'result_cint_n_4.gdx'),
    ('5', 'result_cint_n_5.gdx'),
    ('bau_lo', 'result_urban_exo_lessGDP.gdx'),
    ('3_lo', 'result_cint_n_3_lessGDP.gdx'),
    ('4_lo', 'result_cint_n_4_lessGDP.gdx'),
    ('5_lo', 'result_cint_n_5_lessGDP.gdx'),
    ]

raw = OrderedDict()
extra = dict()
for case, fn in FILES:
    raw[case] = gdx.File('gdx/' + fn)
    extra[case] = gdx.File('gdx/' + fn.replace('.gdx', '_extra.gdx'))

CREM = raw['bau']
cases = pd.Index(raw.keys(), name='case')
time = pd.Index(filter(lambda t: int(t) <= 2030, CREM.set('t')))


# In[16]:

# List of all the parameters available in each file
#CREM.parameters()


# In[55]:

arrays = {}

def label(variable, desc, unit_long, unit_short):
    arrays[variable].attrs.update({'desc': desc, 'unit_long': unit_long,
                                   'unit_short': unit_short})


# In[56]:

# GDP
temp = [raw[case].extract('gdp_ref') for case in cases]
arrays['GDP'] = xray.concat(temp, dim=cases).sel(rs=CREM.set('r'))                     .rename({'rs': 'r'})
label('GDP', 'Gross domestic product',
      'billions of U.S. dollars, constant at 2007', '10⁹ USD')


# In[57]:

# CO2 emissions
temp = []
for case in cases:
    temp.append(raw[case].extract('sectem').sum('g') +
        raw[case].extract('houem'))
arrays['CO2_emi'] = xray.concat(temp, dim=cases)
label('CO2_emi', 'Annual CO₂ emissions',
      'millions of tonnes of CO₂', 'Mt')


# In[60]:

# Air pollutant emissions
temp = []
for case in cases:
    temp.append(raw[case].extract('urban').sum('*'))
temp = xray.concat(temp, dim=cases).sel(rs=CREM.set('r')).rename({'rs': 'r'})
for u in temp['urb']:
    if u in ['PM10', 'PM25']:
        continue
    var_name = '{}_emi'.format(u.values)
    arrays[var_name] = temp.sel(urb=u).drop('urb')
    u_fancy = str(u.values).translate({'2': '₂', '3': '₃'})
    label(var_name, 'Annual {} emissions'.format(u_fancy),
          'millions of tonnes of ' + str(u_fancy), 'Mt')


# In[62]:

# CO₂ price
temp = []
for case in cases:
    temp.append(extra[case].extract('ptcarb_t'))
arrays['CO2_price'] = xray.concat(temp, dim=cases)
label('CO2_price', 'Price of CO₂ emissions permit',
      '2007 US dollars per tonne CO₂', '2007 USD/t')


# In[67]:

# Consumption
temp = []
for case in cases:
    temp.append(extra[case].extract('cons_t'))
arrays['cons'] = xray.concat(temp, dim=cases)
label('cons', 'Household consumption',
      'billions of U.S. dollars, constant at 2007', '10⁹ USD')


# In[72]:

# Primary energy
temp = []
for case in cases:
    temp.append(extra[case].extract('pe_t'))
temp = xray.concat(temp, dim=cases).sel(t=time)
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
    arrays[var_name] = temp.sel(e=ener).drop('e')
    label(var_name, 'Primary energy from {}'.format(e_name[str(ener.values)]),
          'Millions of tonnes of coal equivalent', 'Mtce')


# In[102]:

# TODO population
# FIXME this is a placeholder
arrays['pop'] = arrays['GDP']
label('pop', 'Population', 'Millions', '10⁶')


# In[103]:

# TODO share of coal in production inputs
# FIXME this is a placeholder
arrays['COL_share'] = arrays['COL_energy'] / arrays['GDP']
label('COL_share', 'Value share of coal in industrial production',
      '(unitless)', '0')


# In[104]:

# TODO population-weighted PM2.5 exposure
arrays['PM2.5_exposure'] = arrays['GDP']
label('PM2.5_exposure', 'Population-weighted exposure to PM2.5',
      'micrograms per cubic metre', 'μg/m³')


# In[105]:

# Combine all variables into a single xray.Dataset and truncate time
data = xray.Dataset(arrays).sel(t=time)

data['scenarios'] = (('case',), (
    'BAU: Business-as-usual',
    'Policy: Reduce carbon-intensity of GDP by 3%/year from BAU',
    'Policy: Reduce carbon-intensity of GDP by 4%/year from BAU',
    'Policy: Reduce carbon-intensity of GDP by 5%/year from BAU',
    'LO: BAU with 1% lower annual GDP growth',
    'Policy: Reduce carbon-intensity of GDP by 3%/year from LO',
    'Policy: Reduce carbon-intensity of GDP by 4%/year from LO',
    'Policy: Reduce carbon-intensity of GDP by 5%/year from LO',
    ))

# TODO construct data for low-ammonia cases
base_cases = [str(name.values) for name in data['case']] 
nh3_cases = [name + '_nh3' for name in base_cases]
d = xray.Dataset(coords={'case': nh3_cases})
data.merge(d, join='outer', inplace=True)

# National totals
national = data.sum('r')


# In[106]:

# Output a file with scenario information
data['scenarios'].to_dataframe().to_csv(join(OUT_DIR, 'scenarios.csv'),
                                        header=['description'],
                                        quoting=csv.QUOTE_ALL)


# In[107]:

# Output a file with variable information
var_info = pd.DataFrame(index=[d for d in data.data_vars if d != 'scenarios'],
                        columns=['desc', 'unit_long', 'unit_short'],
                       dtype=str)
print('Missing dimension info:')
for name, _ in var_info.iterrows():
    try:
        row = [data[name].attrs[k] for k in var_info.columns]
    except KeyError:
        print(' ', name)
        continue
    var_info.loc[name,:] = row
var_info.to_csv(join(OUT_DIR, 'variables.csv'), index_label='Variable',
                quoting=csv.QUOTE_ALL)


# In[108]:

# Create directories
for r in CREM.set('r'):
    mkdir(join(OUT_DIR, r), exist_ok=True)
mkdir(join(OUT_DIR, 'national'), exist_ok=True)

# Serialize to CSV
for c in cases:
    # Provincial data
    for r in CREM.set('r'):
        data.sel(case=c, r=r).drop(['case', 'r']).to_dataframe().to_csv(
            join(OUT_DIR, r, '{}.csv'.format(c)))
    # National data
    national.sel(case=c).drop('case').to_dataframe()             .to_csv(join(OUT_DIR, 'national', '{}.csv'.format(c)))

