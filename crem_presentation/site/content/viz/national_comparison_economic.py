# -*- coding: utf-8 -*- #
from bokeh.embed import components

from ._charts import (
    get_pm25_national_plot,
    get_co2_national_plot,
    get_nonfossil,
    add_lo_economic_growth_lines,
)
from .__utils import env


def render():
    plot_params = dict(plot_width=700, grid=True, end_factor=6)
    co2, _ = get_co2_national_plot(**plot_params)
    co2, _ = add_lo_economic_growth_lines(co2, 'CO2_emi')
    pm25, _ = get_pm25_national_plot(**plot_params)
    pm25, _ = add_lo_economic_growth_lines(pm25, 'PM25_conc')
    nonfossil = get_nonfossil(include_bau=True, **plot_params)
    nonfossil, _ = add_lo_economic_growth_lines(nonfossil, 'energy_nonfossil_share')
    template = env.get_template('viz/comparison_national_economic_growth.html')
    script, div = components(
        dict(co2=co2, pm25=pm25, nonfossil=nonfossil),
        wrap_plot_info=False
    )
    return template.render(plot_script=script, plot_div=div)
