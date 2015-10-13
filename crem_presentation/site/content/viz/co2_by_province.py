# -*- coding: utf-8 -*- #
from bokeh.embed import components

from .charts import get_provincial_scenario_line_plot
from .maps import get_province_maps_by_parameter, _add_region_callback
from .utils import env


def render():
    plot, col_province_map, province_map, region_map = _get()
    template = env.get_template('viz/co2_by_province.html')
    script, div = components(
        dict(plot=plot, col_province_map=col_province_map, province_map=province_map, region_map=region_map),
        wrap_plot_info=False
    )
    return template.render(plot_script=script, plot_div=div)


def _get():
    parameter = 'CO2_emi'
    region_map, province_map, col_province_map, source, data = get_province_maps_by_parameter(
        parameter=parameter, parameter_name="CO₂"
    )
    plot, source = get_provincial_scenario_line_plot(
        parameter=parameter, y_ticks=[0, 450, 900], plot_width=600, source=source, data=data,
    )
    region_map = _add_region_callback(region_map, source)
    return (plot, col_province_map, province_map, region_map)
