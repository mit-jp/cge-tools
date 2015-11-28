# -*- coding: utf-8 -*- #
from bokeh.models import HoverTool, Patches, ColumnDataSource, Rect, Text
from .constants import map_legend_x, map_legend_y
from ._data import (
    convert_provincial_dataframe_to_map_datasource,
    get_coal_share_in_2010_by_province,
    get_population_in_2010_by_province,
    get_gdp_delta_in_2030_by_province,
    get_gdp_in_2010_by_province,
    get_co2_2030_4_vs_bau_change_by_province,
    get_2030_pm25_exposure_by_province,
    get_pm25_2030_4_vs_bau_change_by_province,
)
from .__utils import get_map_plot


def get_co2_2030_4_vs_bau_change_map(plot_width=600):
    df, legend_data = get_co2_2030_4_vs_bau_change_by_province(prefix='co2_change', cmap_name='Oranges')
    source, tibet_source = convert_provincial_dataframe_to_map_datasource(df)
    return _get_provincial_map(plot_width, source, tibet_source, legend_data, fill_color='co2_change_color', tooltip_text='Change in CO₂: @co2_change_val{0} Mt (@co2_change_percent{0.00}%)')


def get_col_2010_map(plot_width=600):
    df, legend_data = get_coal_share_in_2010_by_province(prefix='col_2010')
    source, tibet_source = convert_provincial_dataframe_to_map_datasource(df)
    return _get_provincial_map(plot_width, source, tibet_source, legend_data, fill_color='col_2010_color', tooltip_text='Coal share: @col_2010_val{0.0}%')


def get_pm25_2030_4_vs_bau_change_map(plot_width=600):
    df, legend_data = get_pm25_2030_4_vs_bau_change_by_province(prefix='pm25_change', cmap_name='Greens')
    source, tibet_source = convert_provincial_dataframe_to_map_datasource(df)
    return _get_provincial_map(plot_width, source, tibet_source, legend_data, fill_color='pm25_change_color', tooltip_text='Change in PM2.5: @pm25_change_val{0.0} μg/m³ (@pm25_change_percent{0.00}%)')


def get_2030_pm25_exposure_map(plot_width=600):
    df, legend_data = get_2030_pm25_exposure_by_province(prefix='pm25exposure_2030', cmap_name='Purples')
    source, tibet_source = convert_provincial_dataframe_to_map_datasource(df)
    return _get_provincial_map(plot_width, source, tibet_source, legend_data, fill_color='pm25exposure_2030_color', tooltip_text='Weighted exposure: @pm25exposure_2030_val μg/m³')


def get_provincial_pop_2010_map(plot_width=600):
    pop_df, legend_data = get_population_in_2010_by_province(prefix='pop_2010', cmap_name='Purples')
    source, tibet_source = convert_provincial_dataframe_to_map_datasource(pop_df)
    pop_map = _get_provincial_map(plot_width, source, tibet_source, legend_data, fill_color='pop_2010_color', tooltip_text='Population: @pop_2010_val{0} million')
    return pop_map


def get_gdp_2010_map(plot_width=600):
    df, legend_data = get_gdp_in_2010_by_province(prefix='gdp_2010', cmap_name='Greys')
    source, tibet_source = convert_provincial_dataframe_to_map_datasource(df)
    return _get_provincial_map(plot_width, source, tibet_source, legend_data, fill_color='gdp_2010_color', tooltip_text='2010 GDP: @gdp_2010_val{0} bn$')


def get_gdp_delta_in_2030_map(plot_width=600):
    df, legend_data = get_gdp_delta_in_2030_by_province(prefix='gdpdelta_change', cmap_name='Greys')
    source, tibet_source = convert_provincial_dataframe_to_map_datasource(df)
    return _get_provincial_map(plot_width, source, tibet_source, legend_data, fill_color='gdpdelta_change_color', tooltip_text='Change in GDP: @gdpdelta_change_val{0.0}%')


def _get_provincial_map(
    plot_width, source, tibet_source, legend_data, fill_color,
    line_color='black', line_width=0.5, tooltip_text=''
):
    p_map = get_map_plot(plot_width)
    provinces = Patches(
        xs='xs',
        ys='ys',
        fill_color=fill_color,
        line_color=line_color,
        line_width=line_width,
        line_join='round',
    )
    pr = p_map.add_glyph(source, provinces)
    tibet = Patches(
        xs='xs',
        ys='ys',
        fill_color='white',
        line_color='gray',
        line_dash='dashed',
        line_width=0.5,
    )
    tr = p_map.add_glyph(tibet_source, tibet)

    # Add legend
    legend_source = ColumnDataSource(legend_data)
    rect = Rect(
        x='x',
        y=map_legend_y,
        height=1,
        width=0.3,
        fill_color='color',
        line_color=None,
    )
    p_map.add_glyph(legend_source, rect)
    # Add start val
    text_start = [legend_data.vals[0][:-2]]
    p_map.add_glyph(
        ColumnDataSource(
            dict(x=[map_legend_x], y=[map_legend_y - 3.5], text=text_start)
        ), Text(x='x', y='y', text='text', text_font_size='8pt', text_align='left')
    )
    # Add end val
    text_end = [legend_data.vals[99][:-2]]
    if len(text_end[0]) > 5:
        text_end = [legend_data.vals[99][0:5]]
    p_map.add_glyph(
        ColumnDataSource(
            dict(x=[map_legend_x + 25], y=[map_legend_y - 3.5], text=text_end)
        ), Text(x='x', y='y', text='text', text_font_size='8pt', text_align='right')
    )

    # Add hovers
    tooltips = "<span class='tooltip-text'>@name_en</span>"
    tooltips = tooltips + "<span class='tooltip-text'>%s</span>" % tooltip_text
    p_map.add_tools(HoverTool(tooltips=tooltips, renderers=[pr]))
    tibet_tooltips = "<span class='tooltip-text'>@name_en (No data)</span>"
    p_map.add_tools(HoverTool(tooltips=tibet_tooltips, renderers=[tr]))

    return p_map
