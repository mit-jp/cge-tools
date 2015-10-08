# -*- coding: utf-8 -*- #
import pandas as pd
import numpy as np

from bokeh.models import ColumnDataSource
from matplotlib import pyplot
from matplotlib.colors import rgb2hex
from .scenarios import provinces, scenarios, file_names


def get_national_data(parameter):
    read_props = dict(usecols=['t', parameter])
    sources = {}
    data = []
    for scenario in scenarios:
        sources[scenario] = ColumnDataSource(
            pd.read_csv('../cecp-cop21-data/national/%s.csv' % file_names[scenario], **read_props)
        )
        data.extend(sources[scenario].data[parameter])
    data = np.array(data)
    return (sources, data)


def get_provincial_data(parameter):
    """
    Return the provincial datasets for the 4% scencario
    """
    read_props = dict(usecols=['t', parameter])
    dfs = {}
    sources = {}
    data = []
    for province in provinces.keys():
        df = pd.read_csv('../cecp-cop21-data/%s/4.csv' % province, **read_props)
        df['region'] = provinces[province]
        dfs[province] = df
        data.extend(df[parameter])
        sources[province] = ColumnDataSource(df)
    data = np.array(data)
    return (dfs, sources, data)


def get_delta(df, parameter):
    df = df.set_index('t')
    start = df[parameter][2007]
    end = df[parameter][2030]
    return end - start


def normalize(df, column):
    series = df[column]
    norm = np.linalg.norm(series)
    if norm == 0:
        return series
    return series / norm


def get_provincial_change_map_data(parameter):
    dfs, sources, data = get_provincial_data(parameter)
    df = pd.DataFrame({'region': list(provinces.values())}, index=provinces.keys())
    df['delta'] = np.NaN
    for province in provinces.keys():
        df.loc[province, 'delta'] = get_delta(dfs[province], parameter)
    df['delta_norm'] = normalize(df, 'delta')
    df['region_norm'] = df.groupby('region').delta_norm.transform('mean')

    # Add in a 'No Data' row for tibet
    df.loc['XZ', 'delta'] = 'No Data'
    df.loc['XZ', 'region'] = 'west'

    # Get colors for the normalized deltas
    colormap = pyplot.get_cmap('Greys')
    df['delta_color'] = df['delta_norm'].apply(colormap)
    df['delta_color'] = df['delta_color'].apply(rgb2hex)
    df['region_color'] = df['region_norm'].apply(colormap)
    df['region_color'] = df['region_color'].apply(rgb2hex)

    province_info = pd.read_hdf('content/viz/province_map_data_simplified.hdf', 'df')
    province_info = province_info.set_index('alpha')

    map_df = pd.concat([df, province_info], axis=1)
    df = map_df[map_df.index != 'XZ']
    tibet_df = map_df[map_df.index == 'XZ']
    return (ColumnDataSource(df), ColumnDataSource(tibet_df))
