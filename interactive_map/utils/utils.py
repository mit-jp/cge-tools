import pandas as pd
import numpy as np


def get_map_df():
    map_data = pd.read_json('data/province_map_data.json')

    def convert_none_to_np_nan(r):
        r['xs'] = np.array(r['xs'], dtype=float)
        r['ys'] = np.array(r['ys'], dtype=float)
        return r

    map_data = map_data.apply(convert_none_to_np_nan, axis=1)
    return map_data
