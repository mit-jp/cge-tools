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
    # Widgets
    TextInput, CustomJS
)
from bokeh.properties import value

from .utils import get_y_range, get_year_range, get_axis, get_js_array
from .scenarios import colors, names, scenarios, file_names


def get_national_scenario_line_plot(parameter=None, y_ticks=None, plot_width=1200):
    assert parameter
    assert y_ticks

    read_props = dict(usecols=['t', parameter])
    sources = {}
    data = []
    for scenario in scenarios:
        sources[scenario] = ColumnDataSource(
            pd.read_csv('../cecp-cop21-data/national/%s.csv' % file_names[scenario], **read_props)
        )
        data.extend(sources[scenario].data[parameter])
    data = np.array(data)

    plot = Plot(
        x_range=get_year_range(), y_range=get_y_range(data),
        responsive=True, plot_width=plot_width,
        toolbar_location=None, outline_line_color=None,
        min_border=0

    )
    y_ticker = FixedTicker(ticks=y_ticks)
    y_formatter = NumeralTickFormatter(format="0,0")
    y_axis = get_axis(ticker=y_ticker, formatter=y_formatter)
    x_ticker = FixedTicker(ticks=[2007, 2030])
    x_formatter = NumeralTickFormatter(format="0")
    x_axis = get_axis(ticker=x_ticker, formatter=x_formatter, axis_label='')

    plot.add_layout(y_axis, 'left')
    plot.add_layout(x_axis, 'below')
    hit_renderers = []
    line_renderers = {}
    for scenario in scenarios:
        source = sources[scenario]
        if scenario == 'four':
            line_alpha = 0.8
        else:
            line_alpha = 0.1
        line = Line(
            x='t', y=parameter, line_color=colors[scenario],
            line_width=4, line_cap='round', line_join='round', line_alpha=line_alpha
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

        hit_renderer = plot.add_glyph(source, hit_target)
        hit_renderers.append(hit_renderer)
        line_renderer = plot.add_glyph(source, line)
        line_renderers[scenario] = line_renderer
        plot.add_glyph(source, circle)
        plot.add_glyph(scenario_label)

    plot.add_tools(HoverTool(tooltips="@%s{0,0} (@t)" % parameter, renderers=hit_renderers))
    return (plot, line_renderers)
