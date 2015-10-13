# -*- coding: utf-8 -*- #
from bokeh.embed import components

from .charts import get_provincial_scenario_line_plot
from .maps import (
    get_province_maps_by_parameter,
    get_provincial_pop_2030_map,
    get_provincial_pm25_conc_2030_map,
    get_provincial_pm25_exp_2030_map,
    _add_region_callback
)
from .utils import env


def render_he_maps():
    pop_map = get_provincial_pop_2030_map()
    pm25_conc_map = get_provincial_pm25_conc_2030_map()
    pm25_exp_map = get_provincial_pm25_exp_2030_map()
    template = env.get_template('viz/health_impacts_maps.html')
    script, div = components(
        dict(pop_map=pop_map, conc_map=pm25_conc_map, exp_map=pm25_exp_map),
        wrap_plot_info=False
    )
    return template.render(plot_script=script, plot_div=div)


def render_col_map():
    plot, col_province_map, province_map, region_map = _get()
    template = env.get_template('viz/health_impacts_by_province.html')
    script, div = components(
        dict(plot=plot, col_province_map=col_province_map, province_map=province_map, region_map=region_map),
        wrap_plot_info=False
    )
    return template.render(plot_script=script, plot_div=div)


def _get():
    parameter = 'PM25_exposure'
    region_map, province_map, col_province_map, source, data = get_province_maps_by_parameter(
        parameter=parameter, parameter_name='PM2.5 exposure'
    )
    plot, source = get_provincial_scenario_line_plot(
        parameter=parameter, y_ticks=[0, 450, 900], plot_width=600, source=source, data=data,
    )
    region_map = _add_region_callback(region_map, source)
    return (plot, col_province_map, province_map, region_map)
