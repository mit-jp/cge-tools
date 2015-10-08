# -*- coding: utf-8 -*- #
from bokeh.models import (
    # Core
    Plot, Range1d, Grid,
    # Glyph
    Line, Text, Circle,
    # Axes
    FixedTicker, NumeralTickFormatter,
    # Tools
    HoverTool,
)
from bokeh.properties import value

from .utils import get_y_range, get_year_range, get_axis
from .constants import scenarios_colors as colors, names, scenarios, provinces

def render():
    return 'hello world'
