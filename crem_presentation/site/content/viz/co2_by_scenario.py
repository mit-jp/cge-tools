# -*- coding: utf-8 -*- #
import pandas as pd
import numpy as np
from bokeh.models import (
    # Core
    Plot, ColumnDataSource,
    # Glyph
    Line, Text, Circle,
    # Axes
    FixedTicker, NumeralTickFormatter,
    # Tools
    HoverTool,
)
from bokeh.properties import value
from jinja2 import Template
from bokeh.embed import components

from .utils import get_y_range, get_year_range, get_axis, get_js_array
from .scenarios import colors, names, scenarios, file_names


def _get():
    parameter = 'CO2_emi'
    read_props = dict(usecols=['t', parameter])
    sources = {}
    data = []
    for scenario in scenarios:
        # TODO - Use a DATADIR
        sources[scenario] = ColumnDataSource(
            pd.read_csv('../cecp-cop21-data/national/%s.csv' % file_names[scenario], **read_props)
        )
        data.extend(sources[scenario].data[parameter])
    data = np.array(data)

    plot = Plot(
        x_range=get_year_range(), y_range=get_y_range(data),
        responsive=True, plot_width=1200,
        toolbar_location=None, outline_line_color=None,
        min_border=0

    )
    y_ticker = FixedTicker(ticks=[7000, 10000, 13000, 16000])
    y_formatter = NumeralTickFormatter(format="0,0")
    y_axis = get_axis(ticker=y_ticker, formatter=y_formatter, axis_label='CO₂ emissions')
    x_ticker = FixedTicker(ticks=[2007, 2030])
    x_formatter = NumeralTickFormatter(format="0")
    x_axis = get_axis(ticker=x_ticker, formatter=x_formatter, axis_label='')

    plot.add_layout(y_axis, 'left')
    plot.add_layout(x_axis, 'below')
    hit_renderers = []
    line_renderers = {}
    for scenario in scenarios:
        source = sources[scenario]
        if scenario == 'four':
            line_alpha = 0.8
        else:
            line_alpha = 0.1
        line = Line(
            x='t', y=parameter, line_color=colors[scenario],
            line_width=4, line_cap='round', line_join='round', line_alpha=line_alpha
        )
        circle = Circle(
            x='t', y=parameter, size=8,
            line_color=colors[scenario], line_width=2,
            fill_color='white'
        )
        # invisible circle used for hovering
        hit_target = Circle(
            x='t', y=parameter, size=20,
            line_color=None,
            fill_color=None
        )
        scenario_label = Text(
            x=value(source.data['t'][-1] + 0.5), y=value(source.data[parameter][-1]), text=value(names[scenario]),
            text_color=colors[scenario]
        )

        hit_renderer = plot.add_glyph(source, hit_target)
        hit_renderers.append(hit_renderer)
        line_renderer = plot.add_glyph(source, line)
        line_renderers[scenario] = line_renderer
        plot.add_glyph(source, circle)
        plot.add_glyph(scenario_label)

    plot.add_tools(HoverTool(tooltips="@%s{0,0} (@t)" % parameter, renderers=hit_renderers))
    from bokeh.models import TextInput, CustomJS
    line_array = get_js_array(scenarios)
    code = '''
        var lines = %s,
            highlight = cb_obj.get('value').split(',');
        Bokeh.$.each(lines, function(key, line) {
            glyph = line.get('glyph');
            glyph.set('line_alpha', 0.1);
        });
        Bokeh.$.each(highlight, function(i, key) {
            line = lines[key];
            glyph = line.get('glyph');
            glyph.set('line_alpha', 0.8);
        });
    ''' % line_array

    callback = CustomJS(code=code, args=line_renderers)

    text = TextInput(callback=callback)
    return (plot, text)


def render():
    plot, select = _get()

    # Define our html template for out plots
    template = Template('''
        <div class="mdl-color--white mdl-shadow--2dp mdl-cell mdl-cell--9-col mdl-grid">
            <div class="plotdiv" id="{{ plot_div.plot.elementid }}"></div>
            <div class="hidden" id="{{ plot_div.select.elementid }}"></div>
        </div>
        <div class="mdl-color--white mdl-shadow--2dp mdl-cell mdl-cell--3-col mdl-grid">
            <div class="mdl-card__supporting-text">
                <form onchange="Bokeh.custom.form_change(this)">
                    <label for="chk_three" class="mdl-checkbox mdl-js-checkbox mdl-js-ripple-effect">
                        <input type="checkbox" id="chk_three" class="mdl-checkbox__input" />
                        <span class="mdl-checkbox__label">3%</span>
                    </label>
                    <label for="chk_four" class="mdl-checkbox mdl-js-checkbox mdl-js-ripple-effect">
                        <input type="checkbox" id="chk_four" class="mdl-checkbox__input" checked />
                        <span class="mdl-checkbox__label">4%</span>
                    </label>
                    <label for="chk_five" class="mdl-checkbox mdl-js-checkbox mdl-js-ripple-effect">
                        <input type="checkbox" id="chk_five" class="mdl-checkbox__input" />
                        <span class="mdl-checkbox__label">5%</span>
                    </label>
                    <label for="chk_bau" class="mdl-checkbox mdl-js-checkbox mdl-js-ripple-effect">
                        <input type="checkbox" id="chk_bau" class="mdl-checkbox__input" />
                        <span class="mdl-checkbox__label">BAU</span>
                    </label>
                </form>
            </div>
        </div>
        <script type="text/javascript">
            Bokeh.custom = {};
            Bokeh.custom.select_scenario = function(scenario_names) {
                select = Bokeh.index['{{ plot_div.select.modelid }}'];
                select.mset('value', scenario_names);
                select.change_input();
            };
            Bokeh.custom.form_change = function(form) {
                scenarios = '';
                if ( form.chk_three.checked ) {
                    scenarios = scenarios + 'three,';
                }
                if ( form.chk_four.checked ) {
                    scenarios = scenarios + 'four,';
                }
                if ( form.chk_five.checked ) {
                    scenarios = scenarios + 'five,';
                }
                if ( form.chk_bau.checked ) {
                    scenarios = scenarios + 'bau,';
                }
                Bokeh.custom.select_scenario(scenarios);
            };
        </script>
        {{ plot_script }}
    ''')

    script, div = components(dict(plot=plot, select=select), wrap_plot_info=False)
    html = template.render(plot_script=script, plot_div=div)
    return html
