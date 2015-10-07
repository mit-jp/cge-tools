# -*- coding: utf-8 -*- #
from bokeh.models import LinearAxis, Range1d

from jinja2 import Environment, PackageLoader

from .constants import AXIS_FORMATS

env = Environment(loader=PackageLoader('theme', 'templates'))


def get_axis(ticker=None, formatter=None, axis_label=None):
    axis = LinearAxis(axis_label=axis_label, ticker=ticker, formatter=formatter, **AXIS_FORMATS)
    return axis


def get_year_range(end_factor=5):
    return Range1d(2005, 2030 + end_factor)


def get_y_range(data):
    return Range1d(data.min() * 0.80, data.max() * 1.10)


def get_js_array(list_of_keys):
    # See gapminder example for detailed explanation on what this is and why
    # it works:
    # http://nbviewer.ipython.org/github/bokeh/bokeh-notebooks/blob/master/tutorial/A1%20-%20Building%20gapminder.ipynb
    dictionary_of_keys = dict(zip(list_of_keys, list_of_keys))
    js_array = str(dictionary_of_keys).replace("'", "")
    return js_array
