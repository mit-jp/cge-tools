# -*- coding: utf-8 -*- #
from bokeh.embed import components
from bokeh.models import Line, ColumnDataSource, Text

from ._charts import get_co2_national_plot, get_pm25_national_plot, get_nonfossil
from .__utils import env


def render():
    plot_params = dict(plot_width=700, grid=True, end_factor=6)
    co2, _ = get_co2_national_plot(**plot_params)
    pm25, _ = get_pm25_national_plot(**plot_params)
    nonfossil = get_nonfossil(include_bau=True, **plot_params)

    # Add Targets
    pm25.add_glyph(
        ColumnDataSource(data=dict(x=[2010, 2030], y=[35, 35])),
        Line(x='x', y='y', line_width=2, line_dash='dotdash'),
    )
    pm25.add_glyph(
        ColumnDataSource(data=dict(x=[2010.5], y=[33.1], text=['PM2.5 target'])),
        Text(x='x', y='y', text='text', text_font_size='8pt'),
    )

    nonfossil.add_glyph(
        ColumnDataSource(data=dict(x=[2010, 2030], y=[20, 20])),
        Line(x='x', y='y', line_width=2, line_dash='dotdash'),
    )
    nonfossil.add_glyph(
        ColumnDataSource(data=dict(x=[2010.5], y=[20.2], text=['Non-fossil share target'])),
        Text(x='x', y='y', text='text', text_font_size='8pt'),
    )

    template = env.get_template('viz/comparison_national.html')
    script, div = components(
        dict(co2=co2, pm25=pm25, nonfossil=nonfossil),
        wrap_plot_info=False
    )
    return template.render(plot_script=script, plot_div=div)
