# -*- coding: utf-8 -*- #
from bokeh.models import LinearAxis, Range1d, Grid, FixedTicker, NumeralTickFormatter, Plot

from jinja2 import Environment, PackageLoader

from .constants import AXIS_FORMATS, PLOT_FORMATS, grey, dark_grey

env = Environment(loader=PackageLoader('theme', 'templates'))


def get_map_plot(plot_width):
    x_range = [73, 135]
    y_range = [18, 54]
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
        **PLOT_FORMATS
    )
    map_params.update(min_border_top=10)
    return Plot(**map_params)


def get_axis(ticker=None, formatter=None, axis_label=None, color=dark_grey):
    axis = LinearAxis(
        axis_label=axis_label, ticker=ticker, formatter=formatter, major_label_text_color=color,
        **AXIS_FORMATS
    )
    return axis


def add_axes(plot, y_ticks, grid=True, color=None):
    y_ticker = FixedTicker(ticks=y_ticks)
    y_formatter = NumeralTickFormatter(format="0,0")
    y_axis = get_axis(ticker=y_ticker, formatter=y_formatter, color=color)
    x_ticker = FixedTicker(ticks=[2010, 2030])
    five_year_ticker = FixedTicker(ticks=[2010, 2015, 2020, 2025, 2030])
    x_formatter = NumeralTickFormatter(format="0")
    x_axis = get_axis(ticker=x_ticker, formatter=x_formatter, axis_label='', color=color)
    plot.add_layout(y_axis, 'left')
    plot.add_layout(x_axis, 'below')
    if grid:
        x_grid = Grid(
            band_fill_alpha=0.1, band_fill_color=grey,
            dimension=0, ticker=five_year_ticker,
            grid_line_color=None,
        )
        plot.add_layout(x_grid)
    return plot


def get_year_range(end_factor=None):
    if not end_factor:
        end_factor = 5
    return Range1d(2009, 2030 + end_factor)


def get_y_range(data):
    return Range1d(data.min() * 0.80, data.max() * 1.10)


def get_js_array(list_of_keys):
    # See gapminder example for detailed explanation on what this is and why
    # it works:
    # http://nbviewer.ipython.org/github/bokeh/bokeh-notebooks/blob/master/tutorial/A1%20-%20Building%20gapminder.ipynb
    dictionary_of_keys = dict(zip(list_of_keys, list_of_keys))
    js_array = str(dictionary_of_keys).replace("'", "")
    return js_array
