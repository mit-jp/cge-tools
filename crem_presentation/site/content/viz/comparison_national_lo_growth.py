# -*- coding: utf-8 -*- #
from bokeh.embed import components

from .charts import (
    get_national_scenario_line_plot,
    get_lo_national_scenario_line_plot
)
from .utils import env


def render():
    plot_params = dict(plot_width=500, grid=False, end_factor=6)
    co2, _ = get_national_scenario_line_plot(parameter='CO2_emi', y_ticks=[7000, 10000, 13000, 16000], **plot_params)
    pm25, _ = get_national_scenario_line_plot(parameter='PM25_conc', y_ticks=[20, 30, 40], **plot_params)
    nonfossil, _ = get_national_scenario_line_plot(parameter='energy_nonfossil_share', y_ticks=[10, 40, 70], **plot_params)
    co2_lo, _ = get_lo_national_scenario_line_plot(parameter='CO2_emi', y_ticks=[7000, 10000, 13000, 16000], **plot_params)
    pm25_lo, _ = get_lo_national_scenario_line_plot(parameter='PM25_conc', y_ticks=[20, 30, 40], **plot_params)
    nonfossil_lo, _ = get_lo_national_scenario_line_plot(parameter='energy_nonfossil_share', y_ticks=[10, 40, 70], **plot_params)
    template = env.get_template('viz/comparison_national_economic_growth.html')
    script, div = components(
        dict(
            co2=co2, pm25=pm25, nonfossil=nonfossil,
            co2_lo=co2_lo, pm25_lo=pm25_lo, nonfossil_lo=nonfossil_lo
        ),
        wrap_plot_info=False
    )
    return template.render(plot_script=script, plot_div=div)
