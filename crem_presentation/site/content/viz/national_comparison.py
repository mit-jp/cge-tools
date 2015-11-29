# -*- coding: utf-8 -*- #
from bokeh.embed import components
from bokeh.models import TextInput, CustomJS

from .constants import scenarios
from ._charts import get_co2_national_plot, get_pm25_national_plot, get_nonfossil
from .__utils import get_js_array, env


def render():
    plot_params = dict(plot_width=700, grid=True, end_factor=6)
    co2, co2_line_renderers = get_co2_national_plot(**plot_params)
    pm25, pm25_line_renderers = get_pm25_national_plot(**plot_params)
    nonfossil = get_nonfossil(include_bau=True, **plot_params)

    prefixed_line_renderers = {}
    for key in scenarios:
        prefixed_line_renderers['pm25_%s' % key] = pm25_line_renderers[key]
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
            set_alpha(lines['pm25_' + key]);
            set_alpha(lines['co2_' + key]);
        });
    ''' % line_array

    callback = CustomJS(code=code, args=prefixed_line_renderers)
    text = TextInput(callback=callback)

    template = env.get_template('viz/national_comparison.html')
    script, div = components(
        dict(co2=co2, pm25=pm25, nonfossil=nonfossil, text=text),
        wrap_plot_info=False
    )
    return template.render(plot_script=script, plot_div=div)
