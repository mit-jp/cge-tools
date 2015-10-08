# -*- coding: utf-8 -*- #
import pandas as pd
from bokeh.models import HoverTool, TapTool, Patches, CustomJS
from .data import (
    get_provincial_dataframe_with_colored_parameter_delta,
    convert_provincial_dataframe_to_map_datasource,
    get_coal_share_in_2010_by_province,
    get_population_in_2030_by_province,
    get_pm25_conc_in_2030_by_province,
    get_pm25_exposure_in_2030_by_province,
)
from .constants import deep_orange
from .utils import get_map_plot, get_js_array


def get_province_maps_by_parameter(parameter, parameter_name, plot_width=600):
    parameter_df = get_provincial_dataframe_with_colored_parameter_delta(parameter)
    coal_df = get_coal_share_in_2010_by_province(prefix='col_2010')
    df = pd.concat([parameter_df, coal_df], axis=1)

    source, tibet_source = convert_provincial_dataframe_to_map_datasource(df)

    province_map = _get_provincial_map(
        plot_width, source, tibet_source, fill_color='delta_color'
    )
    region_map = _get_provincial_map(
        plot_width, source, tibet_source, fill_color='region_color', selected_line_color=None,
        selected_fill_color=deep_orange, background=True, line_color=None
    )
    col_province_map = _get_provincial_map(
        plot_width, source, tibet_source, fill_color='col_2010_color', selected_line_color='white'
    )

    # Add Tools
    tooltips = "<span class='tooltip-text country'>@name_en</span>"
    province_tooltips = tooltips + "<span class='tooltip-text year'>Change in %s: @delta</span>" % parameter_name
    province_map.add_tools(HoverTool(tooltips=province_tooltips))
    region_tooltips = tooltips + "<span class='tooltip-text year'>@region</span>"
    region_map.add_tools(HoverTool(tooltips=region_tooltips))
    col_province_tooltips = tooltips + "<span class='tooltip-text year'>Coal share in 2010: @col_2010_val</span>"
    col_province_map.add_tools(HoverTool(tooltips=col_province_tooltips))

    return region_map, province_map, col_province_map, source


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


def _add_region_callback(region_map, prefixed_renderers, source):
    js_array = get_js_array(prefixed_renderers.keys())
    code = '''
        var renderers = %s,
            selected = cb_obj.get('selected')['1d']['indices'],
            glyph = null,
            selected_region = source.get('data')['region'][selected],
            regions = source.get('data')['region'],
            indices = [],
            idx = regions.indexOf(selected_region);

        while (idx != -1) {
            indices.push(idx);
            idx = regions.indexOf(selected_region, idx + 1);
        }
        cb_obj.get('selected')['1d']['indices'] = indices;
        source.trigger('change');

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
            Bokeh.$.each(indices, function(i, index) {
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
    tap = region_map.select({'type': TapTool})
    tap.callback = callback
    return region_map


def _get_provincial_map(
    plot_width, source, tibet_source, fill_color,
    selected_fill_color=None, background=False,
    line_color='black', line_width=0.5,
    selected_line_color=deep_orange, selected_line_width=1,
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
    provinces_selected = Patches(
        xs='xs', ys='ys', fill_color=selected_fill_color, line_color=selected_line_color, line_width=selected_line_width, line_join='round',
    )

    patches_renderer = p_map.add_glyph(
        source, provinces, nonselection_glyph=provinces, selection_glyph=provinces_selected
    )

    tibet = Patches(
        xs='xs', ys='ys', fill_color='white', line_color='gray', line_dash='dashed', line_width=0.5,
    )
    p_map.add_glyph(tibet_source, tibet)
    p_map.add_tools(TapTool(renderers=[patches_renderer]))
    return p_map
