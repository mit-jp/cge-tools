from bokeh.models import (
    Plot, Range1d
)


def get_provincial_map(parameter):
    plot = Plot(
        x_range=Range1d(-90, 90),
        y_range=Range1d(-90, 90),
        responsive=True,
        toolbar_location=None,
        outline_line_color=None,
        min_border=0
    )
    return plot
