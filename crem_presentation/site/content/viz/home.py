# -*- coding: utf-8 -*- #
from bokeh.embed import components

from ._maps import get_co2_2030_4_vs_bau_change_map, get_col_2010_map
from .__utils import env


def render():
    template = env.get_template('viz/home_page.html')
    return template.render()
