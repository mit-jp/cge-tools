# -*- coding: utf-8 -*- #
from bokeh.embed import components

from .data import get_energy_mix_for_all_scenarios
from .charts import get_energy_mix_by_scenario
from .utils import env


def render():
    df = get_energy_mix_for_all_scenarios()
    three = get_energy_mix_by_scenario(df, 'three')
    four = get_energy_mix_by_scenario(df, 'four')
    five = get_energy_mix_by_scenario(df, 'five')
    template = env.get_template('viz/energy_mix.html')
    script, div = components(
        dict(three=three, four=four, five=five),
        wrap_plot_info=False
    )
    return template.render(plot_script=script, plot_div=div)
