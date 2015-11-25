# -*- coding: utf-8 -*- #
from bokeh.models import HoverTool, TapTool, Patches, CustomJS
from .data import (
    convert_provincial_dataframe_to_map_datasource,
    get_coal_share_in_2010_by_province,
    get_population_in_2030_by_province,
    get_pm25_conc_in_2030_by_province,
    get_pm25_exposure_in_2030_by_province,
    get_gdp_per_capita_in_2010_by_province,
    get_gdp_delta_change_by_province,
    get_co2_2010_to_2030_change_by_province,
    get_co2_2030_4_vs_bau_change_by_province,
    get_pm25_exposure_change_by_province,
)
from .constants import deep_orange
from .utils import get_map_plot, get_js_array


def get_provincial_pop_2030_map(plot_width=600):
    pop_df = get_population_in_2030_by_province(prefix='pop_2030', cmap_name='Greens')
    source, tibet_source = convert_provincial_dataframe_to_map_datasource(pop_df)
    pop_map = _get_provincial_map(plot_width, source, tibet_source, fill_color='pop_2030_color')
    return pop_map


def get_provincial_pm25_conc_2030_map(plot_width=600):
    df = get_pm25_conc_in_2030_by_province(prefix='pm25_conc_2030', cmap_name='Reds')
    source, tibet_source = convert_provincial_dataframe_to_map_datasource(df)
    return _get_provincial_map(plot_width, source, tibet_source, fill_color='pm25_conc_2030_color')


def get_provincial_pm25_exp_2030_map(plot_width=600):
    df = get_pm25_exposure_in_2030_by_province(prefix='pm25_exp_2030', cmap_name='Greys')
    source, tibet_source = convert_provincial_dataframe_to_map_datasource(df)
    return _get_provincial_map(plot_width, source, tibet_source, fill_color='pm25_exp_2030_color')


def get_col_2010_map(plot_width=600):
    df = get_coal_share_in_2010_by_province(prefix='col_2010')
    source, tibet_source = convert_provincial_dataframe_to_map_datasource(df)
    return _get_provincial_map(plot_width, source, tibet_source, fill_color='col_2010_color', tooltip_text='Coal share: @col_2010_val')


def get_gdp_per_capita_2010_map(plot_width=600):
    df = get_gdp_per_capita_in_2010_by_province(prefix='gdppercap_2010', cmap_name='Purples')
    source, tibet_source = convert_provincial_dataframe_to_map_datasource(df)
    return _get_provincial_map(plot_width, source, tibet_source, fill_color='gdppercap_2010_color')


def get_co2_2010_to_2030_change_map(plot_width=600):
    df = get_co2_2010_to_2030_change_by_province(prefix='co2_change', cmap_name='Oranges')
    source, tibet_source = convert_provincial_dataframe_to_map_datasource(df)
    return _get_provincial_map(plot_width, source, tibet_source, fill_color='co2_change_color', tooltip_text='Change in CO₂: @co2_change_val')


def get_co2_2030_4_vs_bau_change_map(plot_width=600):
    df = get_co2_2030_4_vs_bau_change_by_province(prefix='co2_change', cmap_name='Oranges')
    source, tibet_source = convert_provincial_dataframe_to_map_datasource(df)
    return _get_provincial_map(plot_width, source, tibet_source, fill_color='co2_change_color', tooltip_text='Change in CO₂: @co2_change_val')


def get_pm25_exposure_change_map(plot_width=600):
    df = get_pm25_exposure_change_by_province(prefix='pm25_exp_change', cmap_name='Blues')
    source, tibet_source = convert_provincial_dataframe_to_map_datasource(df)
    return _get_provincial_map(plot_width, source, tibet_source, fill_color='pm25_exp_change_color')


def get_gdp_delta_change_map(plot_width=600):
    df = get_gdp_delta_change_by_province(prefix='gdp_delta_change', cmap_name='Purples')
    source, tibet_source = convert_provincial_dataframe_to_map_datasource(df)
    return _get_provincial_map(plot_width, source, tibet_source, fill_color='gdp_delta_change_color')


def _add_province_callback(province_map, prefixed_renderers, source):
    js_array = get_js_array(prefixed_renderers.keys())
    code = '''
        var renderers = %s,
            selected = cb_obj.get('selected')['1d']['indices'],
            glyph = null;
        Bokeh.$.each(renderers, function(key, r) {
            glyph = r.get('glyph');
            if ( !Bokeh._.isUndefined(glyph) ) {
                glyph.set('line_alpha', 0.5);
                glyph.set('line_width', 1);
                glyph.set('text_alpha', 0.2);
                glyph.set('text_font_style', 'normal');
            }
        });
        window.setTimeout(function(){
            Bokeh.$.each(selected, function(i, index) {
                var key = source.get('data')['index'][index];
                glyph = renderers['line_' + key].get('glyph');
                glyph.set('line_alpha', 0.9);
                glyph.set('line_width', 4);
                glyph = renderers['text_' + key].get('glyph');
                glyph.set('text_alpha', 0.9);
                glyph.set('text_font_style', 'bold');
            });
        }, 20);
    ''' % js_array

    callback = CustomJS(code=code, args=prefixed_renderers)
    callback.args['source'] = source
    tap = province_map.select({'type': TapTool})
    tap.callback = callback
    return province_map


def _add_region_callback(region_map, source):
    code = '''
        var indices = [],
            selected = cb_obj.get('selected')['1d']['indices'],
            selected_region = source.get('data')['region'][selected],
            regions = source.get('data')['region'],
            idx = regions.indexOf(selected_region);
        while (idx != -1) {
            indices.push(idx);
            idx = regions.indexOf(selected_region, idx + 1);
        }
        cb_obj.get('selected')['1d']['indices'] = indices;
        source.trigger('change');
    '''
    callback = CustomJS(code=code, args=dict(source=source))
    tap = region_map.select({'type': TapTool})
    tap.callback = callback
    return region_map


def _get_provincial_map(
    plot_width, source, tibet_source, fill_color,
    selected_fill_color=None, background=False,
    line_color='black', line_width=0.5,
    selected_line_color=deep_orange, selected_line_width=1,
    tooltip_text=''
):
    assert plot_width
    assert source
    assert tibet_source
    assert fill_color

    if not selected_fill_color:
        selected_fill_color = fill_color

    p_map = get_map_plot(plot_width)

    if background:
        bg = Patches(
            xs='xs', ys='ys', fill_color='black', line_color='black', line_width=1
        )
        p_map.add_glyph(source, bg, selection_glyph=bg, nonselection_glyph=bg)

    provinces = Patches(
        xs='xs', ys='ys', fill_color=fill_color, line_color=line_color, line_width=line_width, line_join='round',
    )
    p_map.add_glyph(source, provinces)
    tibet = Patches(
        xs='xs', ys='ys', fill_color='white', line_color='gray', line_dash='dashed', line_width=0.5,
    )
    p_map.add_glyph(tibet_source, tibet)
    tooltips = "<span class='tooltip-text'>@name_en</span>"
    tooltips = tooltips + "<span class='tooltip-text'>%s</span>" % tooltip_text
    p_map.add_tools(HoverTool(tooltips=tooltips))
    return p_map
