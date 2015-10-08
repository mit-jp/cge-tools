# -*- coding: utf-8 -*- #
teal = '#009688'
green = '#4CAF50'
orange = '#FF9800'
deep_orange = '#FF5722'
purple = '#9C27B0'
deep_purple = '#673AB7'
grey = '#9E9E9E'
indigo = '#3F51B5'
dark_grey = '#212121'

AXIS_FORMATS = dict(
    # This is the tick labels (numbers)
    # major_label_text_font=FONT,
    major_label_text_font_size="10pt",
    major_label_text_color=dark_grey,


    # This is this axis label
    # axis_label_text_font=FONT,
    axis_label_text_font_size="12pt",
    axis_label_standoff=30,

    # Lines
    axis_line_color=None,
    axis_line_cap="round",
    axis_line_width=1,

    major_tick_line_width=1,
    major_tick_line_color=None,
    major_tick_line_cap="round",

    # Ticks
    minor_tick_in=None,
    minor_tick_out=None,
    major_tick_in=None,
)

PLOT_FORMATS = dict(
    responsive=True,
    toolbar_location=None,
    outline_line_color=None,
    min_border=0
)
