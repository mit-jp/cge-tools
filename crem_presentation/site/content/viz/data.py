import pandas as pd
import numpy as np

from bokeh.models import ColumnDataSource
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


def get_provincial_change_map_data(parameter):
    dfs, sources, data = get_provincial_data(parameter)

