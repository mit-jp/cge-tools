# -*- coding: utf-8 -*- #
import pandas as pd
import numpy as np

from bokeh.models import ColumnDataSource
from matplotlib import pyplot
from matplotlib.colors import rgb2hex
from .constants import provinces, scenarios, file_names, west


def get_df_and_strip_2007(filename, read_props):
    df = pd.read_csv(filename, **read_props)
    df = df[df.t != 2007]
    return df


def get_national_data(parameter):
    read_props = dict(usecols=['t', parameter])
    sources = {}
    data = []
    for scenario in scenarios:
        df = get_df_and_strip_2007('../cecp-cop21-data/national/%s.csv' % file_names[scenario], read_props)
        sources[scenario] = ColumnDataSource(df)
        data.extend(sources[scenario].data[parameter])
    data = np.array(data)
    return (sources, data)


def get_provincial_dataframes(parameter):
    """
    Return the provincial datasets for the 4% scencario
    """
    read_props = dict(usecols=['t', parameter])
    dfs = {}
    for province in provinces.keys():
        df = get_df_and_strip_2007('../cecp-cop21-data/%s/4.csv' % province, read_props)
        df['region'] = provinces[province]
        dfs[province] = df
    return dfs


def get_provincial_sources_and_yaxis_data(parameter):
    dfs = get_provincial_dataframes(parameter)
    sources = {}
    data = []
    for province in provinces.keys():
        df = dfs[province]
        data.extend(df[parameter])
        sources[province] = ColumnDataSource(df)
    data = np.array(data)
    return sources, data


def get_delta(df, parameter):
    df = df.set_index('t')
    start = df[parameter][2010]
    end = df[parameter][2030]
    return end - start


def normalize_and_color(df, key_value, key_color, cmap_name):
    norm_array = df[key_value] / np.linalg.norm(df[key_value])
    colormap = pyplot.get_cmap(cmap_name)
    norm_map = norm_array.apply(colormap)
    norm_hex = norm_map.apply(rgb2hex)
    df[key_color] = norm_hex
    return df


def get_provincial_dataframe_with_colored_parameter_delta(parameter):
    dfs = get_provincial_dataframes(parameter)
    df = pd.DataFrame({'region': list(provinces.values())}, index=provinces.keys())
    df['delta'] = np.NaN
    for province in provinces.keys():
        df.loc[province, 'delta'] = get_delta(dfs[province], parameter)
    df['region_val'] = df.groupby('region').delta.transform('mean')


    # Get colors for the normalized deltas
    df = normalize_and_color(df, 'delta', 'delta_color', 'Greys')
    df = normalize_and_color(df, 'region_val', 'region_color', 'Greys')

    # Add in a 'No Data' row for tibet
    df.loc['XZ', 'delta'] = 'No Data'
    df.loc['XZ', 'region'] = west

    return df


def convert_provincial_dataframe_to_map_datasource(df):
    province_info = pd.read_hdf('content/viz/province_map_data_simplified.hdf', 'df')
    province_info = province_info.set_index('alpha')

    map_df = pd.concat([df, province_info], axis=1)
    df = map_df[map_df.index != 'XZ']
    tibet_df = map_df[map_df.index == 'XZ']
    return (ColumnDataSource(df), ColumnDataSource(tibet_df))


def get_coal_share_in_2010_by_province(prefix, cmap_name='Blues'):
    parameter = 'COL_share'
    row_index = 2010
    read_props = dict(usecols=['t', parameter])
    key_value = '%s_val' % prefix
    key_color = '%s_color' % prefix

    province_list = provinces.keys()
    n = len(province_list)
    # Create a null dataframe
    df = pd.DataFrame({key_value: np.empty(n), key_color: np.empty(n)}, index=province_list)

    # Populate the values
    for province in province_list:
        four = get_df_and_strip_2007('../cecp-cop21-data/%s/4.csv' % province, read_props)
        four = four.set_index('t')
        df[key_value][province] = four[parameter][row_index]

    df = normalize_and_color(df, key_value, key_color, cmap_name)
    df.loc['XZ', key_value] = 'No Data'
    df.loc['XZ', key_color] = 'white'
    return df
