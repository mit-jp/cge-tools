# -*- coding: utf-8 -*- #
import pandas as pd
import numpy as np

from bokeh.models import ColumnDataSource
from matplotlib import pyplot
from matplotlib.colors import rgb2hex
from .constants import provinces, scenarios, file_names, west, energy_mix_columns


def get_df_and_strip_2007(filename, read_props):
    df = pd.read_csv(filename, **read_props)
    df = df[df.t != 2007]
    return df


def get_lo_national_data(parameter, include_bau):
    return _get_national_data(parameter, '../cecp-cop21-data/national/%s_lo.csv', include_bau)


def get_national_data(parameter, include_bau):
    return _get_national_data(parameter, '../cecp-cop21-data/national/%s.csv', include_bau)


def _get_national_data(parameter, filepath, include_bau):
    read_props = dict(usecols=['t', parameter])
    sources = {}
    data = []
    if not include_bau:
        scenarios.pop(scenarios.index('bau'))
    for scenario in scenarios:
        df = get_df_and_strip_2007(filepath % file_names[scenario], read_props)
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
        df = get_df_and_strip_2007('../cecp-cop21-data/national/%s.csv' % file_names[scenario], read_props)
        all_scenarios['t'] = df['t']
        for energy_mix_column in energy_mix_columns:
            all_scenarios['%s_%s' % (scenario, energy_mix_column)] = df[energy_mix_column]
    return all_scenarios


def get_nonfossil_energy_for_all_scenarios():
    usecols = ['t', 'energy_nonfossil_share']
    read_props = dict(usecols=usecols)
    all_scenarios = pd.DataFrame()
    for scenario in scenarios:
        df = get_df_and_strip_2007('../cecp-cop21-data/national/%s.csv' % file_names[scenario], read_props)
        all_scenarios['t'] = df['t']
        all_scenarios[scenario] = df['energy_nonfossil_share']
    return all_scenarios


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


def get_delta(df, parameter):
    df = df.set_index('t')
    start = df[parameter][2010]
    end = df[parameter][2030]
    return end - start


def normalize_and_color(df, key_value, key_color, cmap_name):
    norm_array = df[key_value] / (np.linalg.norm(df[key_value]))
    norm_array = norm_array * 5  # Beef up the color
    colormap = pyplot.get_cmap(cmap_name)
    norm_map = norm_array.apply(colormap)
    norm_hex = norm_map.apply(rgb2hex)
    df[key_color] = norm_hex
    return df


def get_empty_column():
    return np.zeros((len(provinces.keys()), 1), dtype=object)


def get_provincial_dataframe_with_colored_parameter_delta(parameter):
    dfs = get_provincial_dataframes(parameter)
    df = pd.DataFrame({'region': list(provinces.values())}, index=provinces.keys())
    data = []

    df['delta'] = np.NaN

    df['t'] = get_empty_column()
    df[parameter] = get_empty_column()
    df['text_x'] = get_empty_column()
    df['text_y'] = get_empty_column()
    for province in provinces.keys():
        data.extend(dfs[province][parameter])

        df.set_value(province, 'delta', get_delta(dfs[province], parameter))
        df.set_value(province, 't', list(dfs[province].t.values))
        df.set_value(province, parameter, list(dfs[province][parameter].values))
        df.set_value(province, 'text_x', 2030.2)
        df.set_value(province, 'text_y', list(dfs[province][parameter].values)[-1])

    data = np.array(data)

    df['region_val'] = df.groupby('region').delta.transform('mean')

    # Get colors for the normalized deltas
    df = normalize_and_color(df, 'delta', 'delta_color', 'Greys')
    df = normalize_and_color(df, 'region_val', 'region_color', 'Greys')

    # Add in a 'No Data' row for tibet
    df.loc['XZ', 'delta'] = 'No Data'
    df.loc['XZ', 'region'] = west

    return df, data


def convert_provincial_dataframe_to_map_datasource(df):
    province_info = pd.read_hdf('content/viz/province_map_data_simplified.hdf', 'df')
    province_info = province_info.set_index('alpha')

    map_df = pd.concat([df, province_info], axis=1)
    df = map_df[map_df.index != 'XZ']
    tibet_df = map_df[map_df.index == 'XZ']
    return (ColumnDataSource(df), ColumnDataSource(tibet_df))


def get_coal_share_in_2010_by_province(prefix, cmap_name='Blues'):
    return get_dataframe_of_specific_provincial_data(prefix, cmap_name, 'COL_share', 2010)


def get_population_in_2030_by_province(prefix, cmap_name='Blues'):
    return get_dataframe_of_specific_provincial_data(prefix, cmap_name, 'pop', 2030)


def get_pm25_conc_in_2030_by_province(prefix, cmap_name='Blues'):
    return get_dataframe_of_specific_provincial_data(prefix, cmap_name, 'PM25_conc', 2030)


def get_pm25_exposure_in_2030_by_province(prefix, cmap_name='Blues'):
    return get_dataframe_of_specific_provincial_data(prefix, cmap_name, 'PM25_exposure', 2030)


def get_gdp_per_capita_in_2010_by_province(prefix, cmap_name='Blues'):
    return get_dataframe_of_specific_provincial_data(prefix, cmap_name, 'GDP', 2010)


def get_co2_change_by_province(prefix, cmap_name='Blues'):
    return get_dataframe_of_change_in_provincial_data(prefix, cmap_name, 'GDP')


def get_pm25_exposure_change_by_province(prefix, cmap_name='Blues'):
    return get_dataframe_of_change_in_provincial_data(prefix, cmap_name, 'PM25_exposure')


def get_gdp_delta_change_by_province(prefix, cmap_name='Blues'):
    return get_dataframe_of_change_in_provincial_data(prefix, cmap_name, 'GDP_delta')


def get_dataframe_of_specific_provincial_data(prefix, cmap_name, parameter, row_index):
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


def get_dataframe_of_change_in_provincial_data(prefix, cmap_name, parameter):
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
        df[key_value][province] = get_delta(four, parameter)

    df = normalize_and_color(df, key_value, key_color, cmap_name)
    df.loc['XZ', key_value] = 'No Data'
    df.loc['XZ', key_color] = 'white'
    return df
