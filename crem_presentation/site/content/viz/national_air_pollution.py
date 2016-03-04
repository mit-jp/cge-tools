# -*- coding: utf-8 -*- #
from bokeh.embed import components
from bokeh.models import CustomJS, TextInput

from .constants import scenarios
from ._charts import get_pm25_national_plot, get_co2_national_plot
from .__utils import get_js_array, env


def render():
    co2_plot, ap_plot, text = get()
    template = env.get_template('national_air_pollution.html')
    script, div = components(
        dict(plot1=co2_plot, plot2=ap_plot, text=text),
        wrap_plot_info=False
    )
    return template.render(
        plot_script=script, plot_div=div,
        plot2_title=("Population-weighted PM<sub><small>2.5</small></sub> "
                     "concentrations, μg/m³*"),
        prefix='dual',
    )


def get():
    plot_width = 900
    end_factor = 5
    ap_plot, ap_line_renderers = get_pm25_national_plot(plot_width=plot_width,
                                                        end_factor=end_factor)
    co2_plot, co2_line_renderers = get_co2_national_plot(plot_width=plot_width,
                                                         end_factor=end_factor)
    prefixed_line_renderers = {}
    for key in scenarios:
        prefixed_line_renderers['ap_%s' % key] = ap_line_renderers[key]
        prefixed_line_renderers['co2_%s' % key] = co2_line_renderers[key]

    line_array = get_js_array(prefixed_line_renderers.keys())
    code = '''
        var lines = %s,
            value = cb_obj.get('value'),
            highlight,
            glyph;

        value = value.replace(/(,$)/g, '');
        highlight = value.split(',');
        Bokeh.$.each(lines, function(key, line) {
            glyph = line.get('glyph');
            glyph.set('line_alpha', 0.1);
        });
        Bokeh.$.each(highlight, function(i, key) {
            function set_alpha(line) {
                glyph = line.get('glyph');
                glyph.set('line_alpha', 0.8);
            }
            set_alpha(lines['ap_' + key]);
            set_alpha(lines['co2_' + key]);
        });
    ''' % line_array

    callback = CustomJS(code=code, args=prefixed_line_renderers)
    text = TextInput(callback=callback)
    return (co2_plot, ap_plot, text)
