# -*- coding: utf-8 -*- #
from bokeh.embed import components

from .maps import (
    get_provincial_pop_2030_map,
    get_col_2010_map,
    get_gdp_per_capita_2010_map,
    get_co2_change_map,
    get_pm25_exposure_change_map,
    get_gdp_delta_change_map
)
from .utils import env


def render():
    pop_map = get_provincial_pop_2030_map()
    col_map = get_col_2010_map()
    gdppercap_map = get_gdp_per_capita_2010_map()
    co2_delta_map = get_co2_change_map()
    exp_delta_map = get_pm25_exposure_change_map()
    gdp_delta_map = get_gdp_delta_change_map()
    template = env.get_template('viz/comparison_provincial.html')
    script, div = components(
        dict(
            pop_map=pop_map,
            col_map=col_map,
            gdppercap_map=gdppercap_map,
            co2_delta_map=co2_delta_map,
            exp_delta_map=exp_delta_map,
            gdp_delta_map=gdp_delta_map
        ),
        wrap_plot_info=False
    )
    return template.render(plot_script=script, plot_div=div)
