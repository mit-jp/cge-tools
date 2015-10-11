# -*- coding: utf-8 -*- #
import numpy as np
from bokeh.models import (
    Plot, Range1d, Line, Text, Circle, HoverTool, ColumnDataSource
)
from bokeh.properties import value

from .data import (
    get_provincial_sources_and_yaxis_data,
    get_national_data,
    get_lo_national_data,
    get_coal_share_in_2010_by_province
)
from .utils import get_y_range, get_year_range, add_axes
from .constants import scenarios_colors as colors, names, scenarios, provinces, energy_mix_columns
from .constants_styling import PLOT_FORMATS, deselected_alpha


def get_lo_national_scenario_line_plot(parameter=None, y_ticks=None, plot_width=600, grid=True, end_factor=None):
    assert parameter
    assert y_ticks

    sources, data = get_lo_national_data(parameter)
    return _get_national_scenario_line_plot(sources, data, parameter, y_ticks, plot_width, grid, end_factor)


def get_national_scenario_line_plot(parameter=None, y_ticks=None, plot_width=600, grid=True, end_factor=None):
    assert parameter
    assert y_ticks

    sources, data = get_national_data(parameter)
    return _get_national_scenario_line_plot(sources, data, parameter, y_ticks, plot_width, grid, end_factor)


def _get_national_scenario_line_plot(sources, data, parameter=None, y_ticks=None, plot_width=600, grid=True, end_factor=None):
    plot = Plot(
        x_range=get_year_range(end_factor),
        y_range=get_y_range(data),
        plot_width=plot_width,
        **PLOT_FORMATS
    )
    plot = add_axes(plot, y_ticks, grid=grid)
    hit_renderers = []
    line_renderers = {}
    for scenario in scenarios:
        source = sources[scenario]
        if scenario == 'four':
            line_alpha = 0.8
        else:
            line_alpha = deselected_alpha
        line = Line(
            x='t', y=parameter, line_color=colors[scenario],
            line_width=2, line_cap='round', line_join='round', line_alpha=line_alpha
        )
        circle = Circle(
            x='t', y=parameter, size=4,
            line_color=colors[scenario], line_width=0.5, line_alpha=deselected_alpha,
            fill_color=colors[scenario], fill_alpha=0.6
        )
        # invisible circle used for hovering
        hit_target = Circle(
            x='t', y=parameter, size=20,
            line_color=None, fill_color=None
        )
        scenario_label = Text(
            x=value(source.data['t'][-1] + 1), y=value(source.data[parameter][-1]), text=value(names[scenario]),
            text_color=colors[scenario], text_font_size="8pt",
        )

        hit_renderer = plot.add_glyph(source, hit_target)
        hit_renderers.append(hit_renderer)
        line_renderer = plot.add_glyph(source, line)
        line_renderers[scenario] = line_renderer
        plot.add_glyph(source, circle)
        plot.add_glyph(scenario_label)

    plot.add_tools(HoverTool(tooltips="@%s{0,0} (@t)" % parameter, renderers=hit_renderers))
    return (plot, line_renderers)


def get_energy_mix_by_scenario(df, scenario, plot_width=700):
    data = []
    for energy_mix_column in energy_mix_columns:
        data.extend(df['%s_%s' % (scenario, energy_mix_column)])
    data = np.array(data)
    plot = Plot(
        x_range=get_year_range(end_factor=None),
        y_range=get_y_range(data),
        plot_width=plot_width,
        **PLOT_FORMATS
    )
    plot = add_axes(plot, [100, 1e400])
    source = ColumnDataSource(df)

    hit_renderers = []
    line_renderers = {}

    for energy_mix_column in energy_mix_columns:
        parameter = '%s_%s' % (scenario, energy_mix_column)
        line = Line(
            x='t', y=parameter, line_color='grey',
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
            x=value(source.data['t'][-1] + 0.5), y=value(source.data[parameter][-1]), text=value(energy_mix_column),
            text_color='grey'
        )

        hit_renderer = plot.add_glyph(source, hit_target)
        hit_renderers.append(hit_renderer)
        line_renderer = plot.add_glyph(source, line)
        line_renderers[scenario] = line_renderer
        plot.add_glyph(source, circle)
        plot.add_glyph(scenario_label)

    plot.add_tools(HoverTool(tooltips="@%s{0,0} (@t)" % parameter, renderers=hit_renderers))
    return plot



def get_provincial_scenario_line_plot(parameter=None, y_ticks=None, plot_width=600):
    assert parameter
    assert y_ticks

    sources, data = get_provincial_sources_and_yaxis_data(parameter)
    coal_df = get_coal_share_in_2010_by_province('col_2010')

    plot = Plot(
        x_range=get_year_range(end_factor=2),
        y_range=Range1d(0, data.max() * 1.10),
        plot_width=plot_width,
        **PLOT_FORMATS
    )
    plot = add_axes(plot, y_ticks)

    line_renderers = {}
    text_renderers = {}
    y_offset = data.max() * 0.01

    for province in provinces.keys():
        coal_color = coal_df['col_2010_color'][province]
        source = sources[province]
        line = Line(
            x='t',
            y=parameter,
            line_color=coal_color,
            line_width=2,
            line_cap='round',
            line_join='round',
            line_alpha=0.8,
        )
        province_label = Text(
            x=value(source.data['t'][-1] + 0.2),
            y=value(source.data[parameter][-1] - y_offset),
            text=value(province),
            text_color=coal_color,
            text_font_size='8pt',
            text_alpha=0.8,
        )

        line_renderer = plot.add_glyph(source, line)
        line_renderers[province] = line_renderer
        text_renderer = plot.add_glyph(province_label)
        text_renderers[province] = text_renderer

    return (plot, line_renderers, text_renderers)
