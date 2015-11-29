# -*- coding: utf-8 -*- #
from bokeh.embed import components

from ._maps import get_co2_2030_4_vs_bau_change_map, get_col_2010_map
from .__utils import env


def render():
    co2_map = get_co2_2030_4_vs_bau_change_map()
    col_map = get_col_2010_map()
    template = env.get_template('viz/by_province_co2.html')
    script, div = components(dict(co2_map=co2_map, col_map=col_map), wrap_plot_info=False)
    return template.render(plot_script=script, plot_div=div)
