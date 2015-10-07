# -*- coding: utf-8 -*- #
from bokeh.embed import components
from bokeh.models import TextInput, CustomJS

from .charts import get_national_scenario_line_plot
from .scenarios import scenarios
from .utils import get_js_array, env


def _get():
    plot, line_renderers = get_national_scenario_line_plot(
        parameter='CO2_emi',
        y_ticks=[7000, 10000, 13000, 16000],
    )
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
    plot, text = _get()
    template = env.get_template('viz/one_plot_with_selectors.html')
    script, div = components(dict(plot=plot, text=text), wrap_plot_info=False)
    return template.render(plot_script=script, plot_div=div)
