# -*- coding: utf-8 -*- #
from bokeh.models import (
    Plot, Range1d, Line, Text, Circle, HoverTool, ColumnDataSource, MultiLine,
)
from bokeh.properties import value

from .data import (
    get_national_data,
    get_lo_national_data,
    get_pm25_national_data,
)
from .utils import get_y_range, get_year_range, add_axes
from .constants import scenarios_colors, names, scenarios_no_bau, scenarios, energy_mix_columns
from .constants_styling import PLOT_FORMATS, deselected_alpha, dark_grey


def get_lo_national_scenario_line_plot(parameter=None, y_ticks=None, plot_width=600, grid=True, end_factor=None, y_range=None, include_bau=True):
    assert parameter
    assert y_ticks

    sources, data = get_lo_national_data(parameter, include_bau)
    return _get_national_scenario_line_plot(sources, data, parameter, y_ticks, plot_width, grid, end_factor, y_range)


def get_national_scenario_line_plot(parameter=None, y_ticks=None, plot_width=600, grid=True, end_factor=10, y_range=None, include_bau=True):
    assert parameter
    assert y_ticks

    sources, data = get_national_data(parameter, include_bau)
    return _get_national_scenario_line_plot(sources, data, parameter, y_ticks, plot_width, grid, end_factor, y_range, include_bau)


def _get_national_scenario_line_plot(sources, data, parameter=None, y_ticks=None, plot_width=600, grid=True, end_factor=None, y_range=None, include_bau=True):
    if not y_range:
        y_range = get_y_range(data)

    plot = Plot(
        x_range=get_year_range(end_factor),
        y_range=y_range,
        plot_width=plot_width,
        **PLOT_FORMATS
    )
    plot = add_axes(plot, y_ticks, color=dark_grey, grid=grid)
    hit_renderers = []
    line_renderers = {}
    if include_bau:
        sc = scenarios
    else:
        sc = scenarios_no_bau
    for scenario in sc:
        source = sources[scenario]
        line = Line(
            x='t', y=parameter, line_color=scenarios_colors[scenario],
            line_width=2, line_cap='round', line_join='round'
        )
        circle = Circle(
            x='t', y=parameter, size=4,
            line_color=scenarios_colors[scenario], line_width=0.5, line_alpha=deselected_alpha,
            fill_color=scenarios_colors[scenario], fill_alpha=0.6
        )
        # invisible circle used for hovering
        hit_target = Circle(
            x='t', y=parameter, size=20,
            line_color=None, fill_color=None
        )
        scenario_label = Text(
            x=value(source.data['t'][-1] + 1), y=value(source.data[parameter][-1]), text=value(names[scenario]),
            text_color=scenarios_colors[scenario], text_font_size="8pt",
        )

        hit_renderer = plot.add_glyph(source, hit_target)
        hit_renderers.append(hit_renderer)
        line_renderer = plot.add_glyph(source, line)
        line_renderers[scenario] = line_renderer
        plot.add_glyph(source, circle)
        plot.add_glyph(scenario_label)

    plot.add_tools(HoverTool(tooltips="@%s{0,0} (@t)" % parameter, renderers=hit_renderers))
    return (plot, line_renderers)


def get_pm25_national_plot(plot_width=600, end_factor=None, grid=True):
    sources, data = get_pm25_national_data()
    y_ticks = [30, 40, 50, 60]
    y_range = Range1d(30, 62)
    return _get_national_scenario_line_plot(
        sources, data, 'PM25_conc',
        y_ticks=y_ticks, plot_width=plot_width, grid=grid, end_factor=end_factor, y_range=y_range
    )


def get_nonfossil(plot_width=750, end_factor=5, grid=True, include_bau=False):
    plot, _ = get_national_scenario_line_plot(
        parameter='energy_nonfossil_share',
        y_ticks=[0, 20, 40],
        plot_width=plot_width,
        y_range=Range1d(0, 45),
        grid=grid,
        end_factor=end_factor,
        include_bau=include_bau
    )
    return plot


def get_energy_mix_by_scenario(df, scenario, plot_width=700):
    plot = Plot(
        x_range=get_year_range(end_factor=15),
        y_range=Range1d(0, 4300),
        plot_width=plot_width,
        **PLOT_FORMATS
    )
    plot = add_axes(plot, [0, 2000, 4000], color=scenarios_colors[scenario])
    source = ColumnDataSource(df)

    hit_renderers = []
    line_renderers = {}

    for energy_mix_column in energy_mix_columns.keys():
        parameter = '%s_%s' % (scenario, energy_mix_column)
        line = Line(
            x='t', y=parameter, line_color='black',
            line_width=2, line_cap='round', line_join='round', line_alpha=0.8
        )
        circle = Circle(
            x='t', y=parameter, size=4, fill_color='black', fill_alpha=0.6
        )
        # invisible circle used for hovering
        hit_target = Circle(
            x='t', y=parameter, size=20, line_color=None, fill_color=None
        )
        scenario_label = Text(
            x=value(source.data['t'][-1] + 2), y=value(source.data[parameter][-1] - 200),
            text=value(energy_mix_columns[energy_mix_column]), text_color='grey', text_font_size='8pt',
        )

        hit_renderer = plot.add_glyph(source, hit_target)
        hit_renderers.append(hit_renderer)
        line_renderer = plot.add_glyph(source, line)
        line_renderers[scenario] = line_renderer
        plot.add_glyph(source, circle)
        plot.add_glyph(scenario_label)

    plot.add_tools(HoverTool(tooltips="@%s{0,0} (@t)" % parameter, renderers=hit_renderers))
    return plot


def get_provincial_scenario_line_plot(parameter=None, y_ticks=None, plot_width=600, source=None, data=None):
    plot = Plot(
        x_range=get_year_range(end_factor=2), y_range=Range1d(0, data.max() * 1.10),
        plot_width=plot_width, **PLOT_FORMATS
    )
    plot = add_axes(plot, y_ticks)
    line = MultiLine(
        xs='t', ys=parameter, line_color='col_2010_color',
        line_width=2, line_cap='round', line_join='round', line_alpha=0.8,
    )
    province_label = Text(
        x='text_x', y='text_y', text='index', text_color='col_2010_color',
        text_font_size='8pt', text_alpha=0.8,
    )
    plot.add_glyph(source, line)
    plot.add_glyph(source, province_label)
    return (plot, source)
