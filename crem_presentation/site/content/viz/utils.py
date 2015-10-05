# -*- coding: utf-8 -*- #
from bokeh.models import LinearAxis, Range1d
from .constants import AXIS_FORMATS


def get_axis(ticker=None, formatter=None, axis_label=None):
    axis = LinearAxis(axis_label=axis_label, ticker=ticker, formatter=formatter, **AXIS_FORMATS)
    return axis


def get_year_range():
    return Range1d(2005, 2035)


def get_y_range(data):
    return Range1d(data.min() * 0.80, data.max() * 1.10)
