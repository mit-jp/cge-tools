# -*- coding: utf-8 -*- #
import pandas as pd
import numpy as np
from bokeh.models import (
    # Core
    Plot, ColumnDataSource, Range1d,
    # Glyph
    Line, Text, Circle,
    # Axes
    FixedTicker, NumeralTickFormatter,
    # Tools
    HoverTool,
)
from bokeh.properties import value

from .data import get_provincial_data, get_national_data
from .utils import get_y_range, get_year_range, get_axis
from .scenarios import colors, names, scenarios, file_names, provinces


def get_national_scenario_line_plot(parameter=None, y_ticks=None, plot_width=600):
    assert parameter
    assert y_ticks

    sources, data = get_national_data(parameter)

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


def get_provincial_scenario_line_plot(parameter=None, y_ticks=None, plot_width=600):
    assert parameter
    assert y_ticks

    dfs, sources, data = get_provincial_data(parameter)

    plot = Plot(
        x_range=get_year_range(end_factor=2),
        y_range=Range1d(0, data.max() * 1.10),
        responsive=True,
        plot_width=plot_width,
        toolbar_location=None,
        outline_line_color=None,
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
    line_renderers = {}
    text_renderers = {}
    y_offset = data.max() * 0.01
    for province in provinces.keys():
        source = sources[province]
        line = Line(
            x='t',
            y=parameter,
            line_color='grey',
            line_width=2,
            line_cap='round',
            line_join='round',
            line_alpha=0.2,
        )
        province_label = Text(
            x=value(source.data['t'][-1] + 0.2),
            y=value(source.data[parameter][-1] - y_offset),
            text=value(province),
            text_color='grey',
            text_font_size='8pt',
            text_alpha=0.2,
        )

        line_renderer = plot.add_glyph(source, line)
        line_renderers[province] = line_renderer
        text_renderer = plot.add_glyph(province_label)
        text_renderers[province] = text_renderer

    return (plot, line_renderers, text_renderers)
