# -*- coding: utf-8 -*- #
teal = '#48B4AC'
green = '#4CAF50'
orange = '#FF9800'
deep_orange = '#FF8D64'
purple = '#BC6FC8'
deep_purple = '#673AB7'
grey = '#9E9E9E'
indigo = '#3F51B5'
dark_grey = '#212121'

deselected_alpha = 0.3

AXIS_FORMATS = dict(
    # This is the tick labels (numbers)
    # major_label_text_font=FONT,
    major_label_text_font_size="10pt",
    #major_label_text_color=dark_grey,  # Now set on a method


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
