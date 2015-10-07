from bokeh.models import (
    Plot, Range1d, TapTool, HoverTool, Patches
)

from .data import get_provincial_change_map_data
from .constants import deep_orange


def get_provincial_map(parameter, plot_width=600):
    source = get_provincial_change_map_data(parameter)
    x_range = [70, 140]
    y_range = [10, 60]
    aspect_ratio = (x_range[1] - x_range[0]) / (y_range[1] - y_range[0])
    plot_height = int(plot_width / aspect_ratio)
    x_range = Range1d(x_range[0], x_range[1])
    y_range = Range1d(y_range[0], y_range[1])
    plot = Plot(
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
    tooltips = "<span class='tooltip-text year'>@delta</span>"
    tooltips += "<span class='tooltip-text country'>@name_en</span>"
    plot.add_tools(HoverTool(tooltips=tooltips))
    plot.add_tools(TapTool())

    patches_params = dict(xs='xs', ys='ys', fill_color='delta_color')
    provinces = Patches(line_color='black', line_width=0.5, **patches_params)
    selected_provinces = Patches(line_color=deep_orange, line_width=2, **patches_params)
    plot.add_glyph(source, provinces, nonselection_glyph=provinces, selection_glyph=selected_provinces)
    return plot
