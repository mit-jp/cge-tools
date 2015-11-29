# -*- coding: utf-8 -*- #
from bokeh.models import (
    Plot, Range1d, Line, Text, Circle, HoverTool, ColumnDataSource
)
from bokeh.properties import value

from ._data import get_national_data, get_lo_national_data, get_pm25_national_data
from .__utils import get_y_range, get_year_range, add_axes
from .constants import scenarios_colors, names, scenarios_no_bau, scenarios, energy_mix_columns
from .constants_styling import PLOT_FORMATS, deselected_alpha, dark_grey


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
            x=value(source.data['t'][-1] + 0.8), y=value(source.data[parameter][-1] * 0.98), text=value(names[scenario]),
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


def add_lo_economic_growth_lines(plot, parameter):
    sources, _ = get_lo_national_data(parameter)
    line_renderers = {}
    for scenario in scenarios:
        source = sources[scenario]
        line = Line(
            x='t', y=parameter, line_color=scenarios_colors[scenario],
            line_width=2, line_cap='round', line_join='round', line_dash='dashed'
        )
        line_renderer = plot.add_glyph(source, line)
        line_renderers[scenario] = line_renderer
    return (plot, line_renderers)


def get_pm25_national_plot(plot_width=600, end_factor=None, grid=True):
    sources, data = get_pm25_national_data()
    y_ticks = [30, 40, 50, 60]
    y_range = Range1d(30, 62)
    pm25, line_renderers = _get_national_scenario_line_plot(
        sources, data, 'PM25_conc',
        y_ticks=y_ticks, plot_width=plot_width, grid=grid, end_factor=end_factor, y_range=y_range
    )
    # Add Targets
    pm25.add_glyph(
        ColumnDataSource(data=dict(x=[2010, 2030], y=[35, 35])),
        Line(x='x', y='y', line_width=2, line_dash='dotdash'),
    )
    pm25.add_glyph(
        ColumnDataSource(data=dict(x=[2010.5], y=[33.1], text=['PM2.5 target'])),
        Text(x='x', y='y', text='text', text_font_size='8pt'),
        level='overlay',
    )
    return (pm25, line_renderers)


def get_co2_national_plot(plot_width=600, end_factor=None, grid=True, include_bau=True):
    sources, data = get_national_data('CO2_emi', include_bau)
    y_ticks = [7000, 10000, 13000, 16000]
    y_range = Range1d(7000, 16500)
    return _get_national_scenario_line_plot(
        sources, data, 'CO2_emi',
        y_ticks=y_ticks, plot_width=plot_width, grid=grid,
        end_factor=end_factor, y_range=y_range, include_bau=include_bau
    )


def get_nonfossil(plot_width=750, end_factor=5, grid=True, include_bau=False):
    plot, _ = get_national_scenario_line_plot(
        parameter='energy_nonfossil_share',
        y_ticks=[10, 15, 20, 25],
        plot_width=plot_width,
        y_range=Range1d(8, 29),
        grid=grid,
        end_factor=end_factor,
        include_bau=include_bau
    )
    plot.add_glyph(
        ColumnDataSource(data=dict(x=[2010, 2030], y=[20, 20])),
        Line(x='x', y='y', line_width=2, line_dash='dotdash'),
    )
    plot.add_glyph(
        ColumnDataSource(data=dict(x=[2010.5], y=[20.2], text=['Non-fossil target'])),
        Text(x='x', y='y', text='text', text_font_size='8pt'),
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

    line_renderers = {}

    for energy_mix_column in energy_mix_columns.keys():
        energy_name = energy_mix_columns[energy_mix_column]
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
            x='t', y=parameter, size=10, line_color=None, fill_color=None
        )
        scenario_label = Text(
            x=value(source.data['t'][-1] + 2), y=value(source.data[parameter][-1] - 200),
            text=value(energy_name), text_color='grey', text_font_size='8pt',
        )

        hit_renderer = plot.add_glyph(source, hit_target)
        plot.add_tools(HoverTool(tooltips="%s - @%s{0,0} (@t)" % (energy_name, parameter), renderers=[hit_renderer]))
        plot.add_glyph(source, line)
        plot.add_glyph(source, circle)
        plot.add_glyph(scenario_label)

    return plot
