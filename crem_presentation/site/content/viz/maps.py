# -*- coding: utf-8 -*- #
from bokeh.models import Plot, Range1d, HoverTool, TapTool, Patches
from .data import get_provincial_change_map_data
from .constants import deep_orange


def get_provincial_regional_map(parameter, plot_width=600):
    source, tibet_source = get_provincial_change_map_data(parameter)
    x_range = [70, 140]
    y_range = [10, 60]
    aspect_ratio = (x_range[1] - x_range[0]) / (y_range[1] - y_range[0])
    plot_height = int(plot_width / aspect_ratio)
    x_range = Range1d(x_range[0], x_range[1])
    y_range = Range1d(y_range[0], y_range[1])
    map_params = dict(
        x_range=x_range,
        y_range=y_range,
        title=None,
        plot_width=plot_width,
        plot_height=plot_height,
        outline_line_color=None,
        responsive=True,
        toolbar_location=None,
        min_border=0,
    )
    province_map = Plot(**map_params)
    region_map = Plot(**map_params)

    provinces = Patches(
        xs='xs', ys='ys', fill_color='delta_color', line_color='black', line_width=0.5
    )
    provinces_selected = Patches(
        xs='xs', ys='ys', fill_color='delta_color', line_color=deep_orange, line_width=1, line_join='round',
    )
    regions = Patches(
        xs='xs', ys='ys', fill_color='region_color', line_color=None
    )
    regions_selected = Patches(
        xs='xs', ys='ys', fill_color=deep_orange, line_color=None
    )
    regions_background = Patches(
        xs='xs', ys='ys', fill_color='black', line_color='black', line_width=1
    )
    tibet = Patches(
        xs='xs', ys='ys', fill_color='white', line_color='gray', line_dash='dashed', line_width=0.5,
    )

    patches_renderer = province_map.add_glyph(
        source, provinces, nonselection_glyph=provinces, selection_glyph=provinces_selected
    )
    province_map.add_glyph(tibet_source, tibet)
    region_map.add_glyph(source, regions_background)
    region_map.add_glyph(
        source, regions, nonselection_glyph=regions, selection_glyph=regions_selected
    )
    region_map.add_glyph(tibet_source, tibet)

    # Add Tools
    province_tooltips = "<span class='tooltip-text year'>@delta</span><span class='tooltip-text country'>@name_en</span>"
    province_map.add_tools(HoverTool(tooltips=province_tooltips))
    province_map.add_tools(TapTool(renderers=[patches_renderer]))
    region_tooltips = "<span class='tooltip-text year'>@region</span>"
    region_map.add_tools(HoverTool(tooltips=region_tooltips))
    region_map.add_tools(TapTool())

    return region_map, province_map, source
