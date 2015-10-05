from collections import OrderedDict
from bokeh._legacy_charts import Area
from bokeh.embed import components
from bokeh.palettes import Spectral3
from jinja2 import Template


def _get(width=600):
    xyvalues = OrderedDict(
        python=[2, 3, 7, 5, 26, 221, 44, 233, 254, 265, 266, 267, 120, 111],
        pypy=[12, 33, 47, 15, 126, 121, 144, 233, 254, 225, 226, 267, 110, 130],
        jython=[22, 43, 10, 25, 26, 101, 114, 203, 194, 215, 201, 227, 139, 160],
    )

    area = Area(
        xyvalues, title="Responsive Area Chart",
        xlabel='time', ylabel='memory',
        stacked=True, legend="top_left",
        width=width, palette=Spectral3,
        responsive=True
    )

    return area


def render():
    a1 = _get(900)
    a2 = _get(300)

    # Define our html template for out plots
    template = Template('''<!DOCTYPE html>
        <div class="mdl-color--white mdl-shadow--2dp mdl-cell mdl-cell--6-col mdl-grid">
        {{ plot_div.a1 }}
        </div>
        <div class="mdl-color--white mdl-shadow--2dp mdl-cell mdl-cell--6-col mdl-grid">
        {{ plot_div.a2 }}
        </div>
        {{ plot_script }}
    ''')

    script, div = components(dict(a1=a1, a2=a2))

    html = template.render(plot_script=script, plot_div=div)
    return html
