from collections import OrderedDict
from bokeh._legacy_charts import Area
from bokeh.embed import components
from jinja2 import Template


def _get():
    xyvalues = OrderedDict(
        python=[2, 3, 7, 5, 26, 221, 44, 233, 254, 265, 266, 267, 120, 111],
        pypy=[12, 33, 47, 15, 126, 121, 144, 233, 254, 225, 226, 267, 110, 130],
        jython=[22, 43, 10, 25, 26, 101, 114, 203, 194, 215, 201, 227, 139, 160],
    )

    area = Area(
        xyvalues, title="Responsive Area Chart",
        xlabel='time', ylabel='memory',
        stacked=True, legend="top_left",
        responsive=True
    )

    return area


def render():
    plot = _get()

    # Define our html template for out plots
    template = Template('''<!DOCTYPE html>
        <h5>Resize the window to see some plots resizing</h5>
        <p>Red - pan with responsive</p>
        {{ plot_div }}
        {{ plot_script }}
    ''')

    script, div = components(plot)

    html = template.render(plot_script=script, plot_div=div)
    return html
