# -*- coding: utf-8 -*- #
from bokeh.embed import components
from bokeh.models import Patches

from ._maps import get_co2_2030_4_vs_bau_change_map, get_col_2010_map
from .__utils import env

from os.path import join

def render():
    co2_map, df, _ = get_co2_2030_4_vs_bau_change_map()
    col_map, df, source = get_col_2010_map(df=df)

    # Optimize the data sources
    for gr in co2_map.renderers:
        if isinstance(gr.glyph, Patches):
            gr.data_source = source
            break

    template = env.get_template('by_province_co2.html')
    script, div = components(dict(co2_map=co2_map, col_map=col_map), wrap_plot_info=False)
    return template.render(plot_script=script, plot_div=div)
