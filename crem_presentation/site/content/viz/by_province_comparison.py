# -*- coding: utf-8 -*- #
from bokeh.embed import components
from bokeh.models import Patches

from ._maps import (
    get_provincial_pop_2010_map,
    get_col_2010_map,
    get_gdp_2010_map,
    get_co2_2030_4_vs_bau_change_map,
    get_pm25_2030_4_vs_bau_change_map,
    get_gdp_delta_in_2030_map,
)
from .__utils import env


def render():
    pop_map, df, _ = get_provincial_pop_2010_map()
    col_map, df, _ = get_col_2010_map(df=df)
    gdp_map, df, _ = get_gdp_2010_map(df=df)
    co2_delta_map, df, _ = get_co2_2030_4_vs_bau_change_map(df=df)
    exp_delta_map, df, _ = get_pm25_2030_4_vs_bau_change_map(df=df)
    gdp_delta_map, df, source = get_gdp_delta_in_2030_map(df=df)

    # Optimize the data sources
    for m in [pop_map, col_map, gdp_map, co2_delta_map, exp_delta_map]:
        for gr in m.renderers:
            if isinstance(gr.glyph, Patches):
                gr.data_source = source
                break

    template = env.get_template('viz/by_province_comparison.html')
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
