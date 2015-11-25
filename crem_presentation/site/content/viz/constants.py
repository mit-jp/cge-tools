# -*- coding: utf-8 -*- #
from .constants_styling import *

scenarios = ['three', 'four', 'five', 'bau']
scenarios_no_bau = ['three', 'four', 'five']

names = {
    'three': '3%',
    'four': '4%',
    'five': '5%',
    'bau': 'No policy'
}

file_names = {
    'three': '3',
    'four': '4',
    'five': '5',
    'bau': 'bau'
}

scenarios_colors = {
    'three': teal,
    'four': deep_orange,
    'five': purple,
    'bau': grey
}

west = 'West'
center = 'Center'
east = 'East'

provinces = {
    'BJ': east,
    'TJ': east,
    'HE': center,
    'SX': center,
    'NM': center,
    'LN': center,
    'JL': center,
    'HL': center,
    'SH': east,
    'JS': east,
    'ZJ': east,
    'AH': center,
    'FJ': east,
    'JX': center,
    'SD': east,
    'HA': center,
    'HB': center,
    'HN': center,
    'GD': east,
    'GX': center,
    'HI': east,
    'CQ': center,
    'SC': center,
    'GZ': center,
    'YN': west,
    'SN': west,
    'GS': west,
    'QH': west,
    'NX': west,
    'XJ': west,
}

energy_mix_columns = {
    'OIL_energy': 'Oil',
    'COL_energy': 'Coal',
    'GAS_energy': 'Gas',
    'energy_nonfossil': 'Non-fossil',
}

map_legend_x = 73
map_legend_y = 53
