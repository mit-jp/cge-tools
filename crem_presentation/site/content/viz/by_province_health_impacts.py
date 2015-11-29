# -*- coding: utf-8 -*- #
from bokeh.embed import components
from bokeh.models import Patches

from ._maps import (
    get_pm25_2030_4_vs_bau_change_map,
    get_2030_pm25_exposure_map,
)
from .__utils import env


def render():
    pm25_map, df, _ = get_pm25_2030_4_vs_bau_change_map()
    exposure_map, df, source = get_2030_pm25_exposure_map(df=df)

    # Optimize the data sources
    for gr in pm25_map.renderers:
        if isinstance(gr.glyph, Patches):
            gr.data_source = source
            break

    template = env.get_template('viz/by_province_health_impacts.html')
    script, div = components(
        dict(pm25_map=pm25_map, exposure_map=exposure_map),
        wrap_plot_info=False
    )
    return template.render(plot_script=script, plot_div=div)
