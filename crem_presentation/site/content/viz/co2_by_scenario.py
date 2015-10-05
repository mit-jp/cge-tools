# -*- coding: utf-8 -*- #
import pandas as pd
import numpy as np
from bokeh.models import (
    # Core
    Plot, ColumnDataSource,
    # Glyph
    Line, Text, Circle,
    # Axes
    FixedTicker, NumeralTickFormatter,
    # Tools
    HoverTool,
)
from bokeh.properties import value
from jinja2 import Template
from bokeh.embed import components

from .utils import get_y_range, get_year_range, get_axis
from .scenarios import colors, names, scenarios

def _get():
    parameter = 'CO2_emi'
    read_props = dict(usecols=['t', parameter])
    sources = {}
    data = []
    for scenario in scenarios:
        # TODO - Use a DATADIR
        sources[scenario] = ColumnDataSource(pd.read_csv('../cecp-cop21-data/national/%s.csv' % scenario, **read_props))
        data.extend(sources[scenario].data[parameter])
    data = np.array(data)

    plot = Plot(
        x_range=get_year_range(), y_range=get_y_range(data),
        responsive=True, plot_width=1200,
        toolbar_location=None, outline_line_color=None,
        min_border=0

    )
    y_ticker = FixedTicker(ticks=[7000, 10000, 13000, 16000])
    y_formatter = NumeralTickFormatter(format="0,0")
    y_axis = get_axis(ticker=y_ticker, formatter=y_formatter, axis_label='CO₂ emissions')
    x_ticker = FixedTicker(ticks=[2007, 2030])
    x_formatter = NumeralTickFormatter(format="0")
    x_axis = get_axis(ticker=x_ticker, formatter=x_formatter, axis_label='')

    plot.add_layout(y_axis, 'left')
    plot.add_layout(x_axis, 'below')
    renderers = []
    for scenario in scenarios:
        source = sources[scenario]
        line = Line(
            x='t', y=parameter, line_color=colors[scenario],
            line_width=4, line_cap='round', line_join='round', line_alpha=0.8
        )
        circle = Circle(
            x='t', y=parameter, size=8,
            line_color=colors[scenario], line_width=2,
            fill_color='white'
        )
        # invisible circle used for hovering
        hit_target = Circle(
            x='t', y=parameter, size=20,
            line_color=None,
            fill_color=None
        )
        scenario_label = Text(
            x=value(source.data['t'][-1] + 0.5), y=value(source.data[parameter][-1]), text=value(names[scenario]),
            text_color=colors[scenario]
        )

        renderer = plot.add_glyph(source, hit_target)
        renderers.append(renderer)
        plot.add_glyph(source, line)
        plot.add_glyph(source, circle)
        plot.add_glyph(scenario_label)

    plot.add_tools(HoverTool(tooltips="@%s{0,0} (@t)" % parameter, renderers=renderers))
    return plot


def render():
    plot = _get()

    # Define our html template for out plots
    template = Template('''
        <div class="mdl-color--white mdl-shadow--2dp mdl-cell mdl-cell--12-col mdl-grid">
        {{ plot_div }}
        </div>
        {{ plot_script }}
    ''')

    script, div = components(plot)
    html = template.render(plot_script=script, plot_div=div)
    return html
