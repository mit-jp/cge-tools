# -*- coding: utf-8 -*- #
import pandas as pd
import numpy as np

from bokeh.models import ColumnDataSource
from matplotlib import pyplot
from matplotlib.colors import rgb2hex
from .constants import (
    provinces, scenarios, scenarios_no_bau, file_names, energy_mix_columns, map_legend_x
)

from os.path import join
DATA_DIR = join('..', '..', '..', 'cecp-cop21-data')

def get_lo_national_data(parameter):
    return _get_national_data(parameter, join(DATA_DIR, 'national', '%s_lo.csv'), include_bau=True)


def get_national_data(parameter, include_bau):
    return _get_national_data(parameter, join(DATA_DIR, 'national', '%s.csv'), include_bau)


def get_pm25_national_data():
    filepath = join(DATA_DIR, 'national', '%s.csv')
    parameter = 'PM25_exposure'
    read_props = dict(usecols=['t', parameter])
    sources = {}
    data = []
    for scenario in scenarios:
        df = get_df_and_strip_2007_15_20_25(filepath % file_names[scenario], read_props)
        sources[scenario] = ColumnDataSource(df)
        data.extend(sources[scenario].data[parameter])
    data = np.array(data)
    return (sources, data)


def get_energy_mix_for_all_scenarios():
    usecols = ['t']
    usecols.extend(energy_mix_columns)
    read_props = dict(usecols=usecols)
    all_scenarios = pd.DataFrame()
    for scenario in scenarios:
        df = get_df_and_strip_2007(join(DATA_DIR, 'national', '%s.csv') % file_names[scenario], read_props)
        all_scenarios['t'] = df['t']
        for energy_mix_column in energy_mix_columns:
            all_scenarios['%s_%s' % (scenario, energy_mix_column)] = df[energy_mix_column]
    return all_scenarios


def get_co2_2030_4_vs_bau_change_by_province(prefix, cmap_name='Blues', df=None):
    return get_dataframe_of_2030_4_vs_bau_change_in_provincial_data(prefix, cmap_name, 'CO2_emi', df=df)


def get_coal_share_in_2010_by_province(prefix, cmap_name='Blues', df=None):
    return get_dataframe_of_specific_provincial_data(prefix, cmap_name, 'COL_share', 2010, df=df)


def get_population_in_2010_by_province(prefix, cmap_name='Blues', df=None):
    return get_dataframe_of_specific_provincial_data(prefix, cmap_name, 'pop', 2010, df=df)


def get_gdp_in_2010_by_province(prefix, cmap_name='Blues', df=None):
    return get_dataframe_of_specific_provincial_data(prefix, cmap_name, 'GDP', 2010, df=df)


def get_2030_pm25_exposure_by_province(prefix, cmap_name='Blues', df=None):
    return get_dataframe_of_specific_provincial_data(prefix, cmap_name, 'PM25_exposure', 2030, df=df)


def get_pm25_2030_4_vs_bau_change_by_province(prefix, cmap_name='Blues', df=None):
    return get_dataframe_of_2030_4_vs_bau_change_in_provincial_data(prefix, cmap_name, 'PM25_exposure', df=df)


def _get_dataframe_of_specific_provincial_data(prefix, parameter, row_index, df=None):
    read_props = dict(usecols=['t', parameter])
    key_value = '%s_val' % prefix
    key_color = '%s_color' % prefix

    province_list = provinces.keys()
    n = len(province_list)
    # Create a null dataframe
    null_df = pd.DataFrame({key_value: np.empty(n), key_color: np.empty(n)}, index=province_list)
    if df is not None:
        df = pd.merge(df, null_df, left_index=True, right_index=True)
    else:
        df = null_df
    # Populate the values
    for province in province_list:
        four = get_df_and_strip_2007(join(DATA_DIR, '%s', '4.csv') % province, read_props)
        four = four.set_index('t')
        df[key_value][province] = four[parameter][row_index]

    return (df, key_value, key_color)


def get_dataframe_of_specific_provincial_data(prefix, cmap_name, parameter, row_index, df=None, boost_factor=None):
    if df is not None:
        assert isinstance(df, pd.DataFrame)
    df, key_value, key_color = _get_dataframe_of_specific_provincial_data(prefix, parameter, row_index, df)
    df, legend_data = normalize_and_color(df, key_value, key_color, cmap_name, boost_factor)
    df.loc['XZ', key_value] = 'No Data'
    df.loc['XZ', key_color] = 'white'
    return (df, legend_data)


def get_dataframe_of_2030_4_vs_bau_change_in_provincial_data(prefix, cmap_name, parameter, df=None):
    if df is not None:
        assert isinstance(df, pd.DataFrame)
    read_props = dict(usecols=['t', parameter])
    key_value = '%s_val' % prefix
    key_color = '%s_color' % prefix
    key_percent = '%s_percent' % prefix

    province_list = provinces.keys()
    n = len(province_list)
    # Create a null dataframe
    null_df = pd.DataFrame({key_value: np.empty(n), key_color: np.empty(n), key_percent: np.empty(n)}, index=province_list)
    if df is not None:
        df = pd.merge(df, null_df, left_index=True, right_index=True)
    else:
        df = null_df

    # Populate the values
    for province in province_list:
        four = get_df_and_strip_2007(join(DATA_DIR, '%s', '4.csv') % province, read_props)
        bau = get_df_and_strip_2007(join(DATA_DIR, '%s', 'bau.csv') % province, read_props)
        df[key_value][province], df[key_percent][province] = get_2030_4_vs_bau_delta(four, bau, parameter)

    df, legend_data = normalize_and_color(df, key_value, key_color, cmap_name)
    df.loc['XZ', key_value] = 'No Data'
    df.loc['XZ', key_color] = 'white'
    return (df, legend_data)


def _get_national_data(parameter, filepath, include_bau):
    read_props = dict(usecols=['t', parameter])
    sources = {}
    data = []
    if include_bau:
        sc = scenarios
    else:
        sc = scenarios_no_bau
    for scenario in sc:
        df = get_df_and_strip_2007(filepath % file_names[scenario], read_props)
        sources[scenario] = ColumnDataSource(df)
        data.extend(sources[scenario].data[parameter])
    data = np.array(data)
    return (sources, data)


def get_2030_4_vs_bau_delta(four, bau, parameter):
    four = four.set_index('t')
    bau = bau.set_index('t')
    four = four[parameter][2030]
    bau = bau[parameter][2030]
    absolute = four - bau
    percent = ((four - bau) / bau) * 100
    return (absolute, percent)


def build_legend_data(df, key_value, sign, colormap, boost_factor):
    norm_array = df[key_value]
    val_min = round(norm_array.min())
    val_max = round(norm_array.max())
    if key_value == 'col_2010_val':
        norm_array = norm_array.dropna()
    vals = pd.Series(np.linspace(val_min, val_max, num=100)) * sign
    norm_vals = vals / (np.linalg.norm(norm_array))
    norm_vals = norm_vals * boost_factor
    norm_map = norm_vals.apply(colormap)
    norm_hex = norm_map.apply(rgb2hex)
    df = pd.DataFrame({'vals': vals * sign, 'color': norm_hex}, dtype=str)
    df['x'] = (df.index / 4) + map_legend_x
    return df


def normalize_and_color(df, key_value, key_color, cmap_name, boost_factor=None):
    if not boost_factor:
        boost_factor = 2
    sign = 1
    if df[key_value].max() <= 0:
        sign = -1
    norm_array = df[key_value].copy()
    if key_value == 'col_2010_val':
        norm_array = norm_array.dropna()
    norm_array = norm_array * sign / (np.linalg.norm(norm_array))
    norm_array = norm_array * boost_factor
    colormap = pyplot.get_cmap(cmap_name)
    norm_map = norm_array.apply(colormap)
    norm_hex = norm_map.apply(rgb2hex)
    df[key_color] = norm_hex
    legend_data = build_legend_data(df, key_value, sign, colormap, boost_factor)
    return (df, legend_data)


def convert_provincial_dataframe_to_map_datasource(df):
    province_info = pd.read_hdf(join('content', 'viz', '__province_map_data_simplified.hdf'), 'df')
    province_info = province_info.set_index('alpha')

    map_df = pd.concat([df, province_info], axis=1)
    df = map_df[map_df.index != 'XZ']
    tibet_df = map_df[map_df.index == 'XZ']
    return (ColumnDataSource(df), ColumnDataSource(tibet_df))


def get_df_and_strip_2007(filename, read_props):
    df = pd.read_csv(filename, **read_props)
    df = df[df.t != 2007]
    return df


def get_df_and_strip_2007_15_20_25(filename, read_props):
    df = pd.read_csv(filename, **read_props)
    df = df[(df.t == 2010) | (df.t == 2030)]
    return df


# Handle specially because of outlier value
def _normalize_gdp_delta(vals, dmin, dmax):
    colormap = pyplot.get_cmap('RdYlGn')
    norm_vals = vals * 0.8
    norm_vals = (norm_vals - dmin) / (dmax - dmin + 4)
    norm_map = norm_vals.apply(colormap)
    norm_hex = norm_map.apply(rgb2hex)
    return norm_hex


def get_gdp_delta_in_2030_by_province(prefix, df=None):

    df, key_value, key_color = _get_dataframe_of_specific_provincial_data(prefix, 'GDP_delta', 2030, df=df)
    vals = df[key_value]
    vals.pop('SX')

    dmin = vals.min().round()
    dmax = vals.max().round()

    df[key_color] = _normalize_gdp_delta(vals, dmin, dmax)

    legend_vals = pd.Series(np.linspace(dmin, dmax, num=100))
    legend_hex = _normalize_gdp_delta(legend_vals, dmin, dmax)
    legend_data = pd.DataFrame({'vals': legend_vals, 'color': legend_hex}, dtype=str)
    legend_data['x'] = (legend_data.index / 4) + map_legend_x

    df.loc['XZ', key_value] = 'No Data'
    df.loc['XZ', key_color] = 'white'
    df.loc['SX', key_color] = '#A81625'
    return (df, legend_data)
