# -*- coding: utf-8 -*- #
from bokeh.embed import components

from ._maps import (
    get_pm25_2030_4_vs_bau_change_map,
    get_2030_pm25_exposure_map,
)
from .__utils import env


def render():
    pm25_map = get_pm25_2030_4_vs_bau_change_map()
    exposure_map = get_2030_pm25_exposure_map()
    template = env.get_template('viz/health_impacts_by_province.html')
    script, div = components(
        dict(pm25_map=pm25_map, exposure_map=exposure_map),
        wrap_plot_info=False
    )
    return template.render(plot_script=script, plot_div=div)
