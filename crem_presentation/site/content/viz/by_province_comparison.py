# -*- coding: utf-8 -*- #
from bokeh.embed import components

from ._maps import (
    get_provincial_pop_2030_map,
    get_col_2010_map,
    get_gdp_2010_map,
    get_co2_2030_4_vs_bau_change_map,
    get_pm25_2030_4_vs_bau_change_map,
    get_gdp_delta_in_2030_map,
)
from .__utils import env


def render():
    pop_map = get_provincial_pop_2030_map()
    col_map = get_col_2010_map()
    gdp_map = get_gdp_2010_map()
    co2_delta_map = get_co2_2030_4_vs_bau_change_map()
    exp_delta_map = get_pm25_2030_4_vs_bau_change_map()
    gdp_delta_map = get_gdp_delta_in_2030_map()
    template = env.get_template('viz/comparison_provincial.html')
    script, div = components(
        dict(
            pop_map=pop_map,
            col_map=col_map,
            gdp_map=gdp_map,
            co2_delta_map=co2_delta_map,
            exp_delta_map=exp_delta_map,
            gdp_delta_map=gdp_delta_map
        ),
        wrap_plot_info=False
    )
    return template.render(plot_script=script, plot_div=div)
