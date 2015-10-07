# -*- coding: utf-8 -*- #
import pandas as pd
from bokeh.embed import components
from bokeh.models import TextInput, CustomJS, ColumnDataSource, Line, Circle

from .charts import get_provincial_scenario_line_plot
from .maps import get_provincial_map
from .scenarios import colors, scenarios, file_names, provinces
from .utils import get_js_array, env

def render():
    plot, province_map, text = _get()
    template = env.get_template('viz/co2_by_province.html')
    script, div = components(dict(plot=plot, province_map=province_map, text=text), wrap_plot_info=False)
    return template.render(plot_script=script, plot_div=div)

def _get():
    parameter = 'CO2_emi'
    plot, line_renderers = get_provincial_scenario_line_plot(
        parameter=parameter,
        y_ticks=[0, 450, 900],
        plot_width=500,
    )

    province_map = get_provincial_map(
        parameter=parameter
    )

    line_array = get_js_array(provinces)
    code = '''
        var lines = %s,
            highlight = cb_obj.get('value').split(',');
        Bokeh.$.each(lines, function(key, line) {
            glyph = line.get('glyph');
            glyph.set('line_alpha', 0.1);
        });
        Bokeh.$.each(highlight, function(i, key) {
            function set_alpha(line) {
                glyph = line.get('glyph');
                glyph.set('line_alpha', 0.8);
            }
            set_alpha(lines[key]);
        });
    ''' % line_array

    callback = CustomJS(code=code, args=line_renderers)
    text = TextInput(callback=callback)
    return (plot, province_map, text)
