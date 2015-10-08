# -*- coding: utf-8 -*- #
from bokeh.models import HoverTool, TapTool, Patches
from .data import get_provincial_change_map_data
from .constants import deep_orange
from .utils import get_map_plot


def get_provincial_map(
    plot_width, source, tibet_source, fill_color,
    selected_fill_color=None, background=False,
    line_color='black', line_width=0.5,
    selected_line_color=deep_orange, selected_line_width=1,
):
    assert plot_width
    assert source
    assert tibet_source
    assert fill_color

    if not selected_fill_color:
        selected_fill_color = fill_color

    p_map = get_map_plot(plot_width)

    if background:
        bg = Patches(
            xs='xs', ys='ys', fill_color='black', line_color='black', line_width=1
        )
        p_map.add_glyph(source, bg, selection_glyph=bg, nonselection_glyph=bg)

    provinces = Patches(
        xs='xs', ys='ys', fill_color=fill_color, line_color=line_color, line_width=line_width, line_join='round',
    )
    provinces_selected = Patches(
        xs='xs', ys='ys', fill_color=selected_fill_color, line_color=selected_line_color, line_width=selected_line_width, line_join='round',
    )

    patches_renderer = p_map.add_glyph(
        source, provinces, nonselection_glyph=provinces, selection_glyph=provinces_selected
    )

    tibet = Patches(
        xs='xs', ys='ys', fill_color='white', line_color='gray', line_dash='dashed', line_width=0.5,
    )
    p_map.add_glyph(tibet_source, tibet)
    p_map.add_tools(TapTool(renderers=[patches_renderer]))
    return p_map


def get_co2_by_province_maps(parameter, plot_width=600):
    source, tibet_source = get_provincial_change_map_data(parameter)

    province_map = get_provincial_map(
        plot_width, source, tibet_source, fill_color='delta_color'
    )
    region_map = get_provincial_map(
        plot_width, source, tibet_source, fill_color='region_color', selected_line_color=None,
        selected_fill_color=deep_orange, background=True, line_color=None
    )
    col_province_map = get_provincial_map(
        plot_width, source, tibet_source, fill_color='col_2010_color', selected_line_color='white')

    # Add Tools
    tooltips = "<span class='tooltip-text country'>@name_en</span>"
    province_tooltips = tooltips + "<span class='tooltip-text year'>Change in CO₂: @delta</span>"
    province_map.add_tools(HoverTool(tooltips=province_tooltips))
    region_tooltips = tooltips + "<span class='tooltip-text year'>@region</span>"
    region_map.add_tools(HoverTool(tooltips=region_tooltips))
    col_province_tooltips = tooltips + "<span class='tooltip-text year'>Coal share in 2010: @col_2010_val</span>"
    col_province_map.add_tools(HoverTool(tooltips=col_province_tooltips))

    return region_map, province_map, col_province_map, source
