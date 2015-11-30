# -*- coding: utf-8 -*- #
from bokeh.embed import components

from ._data import get_energy_mix_for_all_scenarios
from ._charts import get_energy_mix_by_scenario, get_nonfossil
from .__utils import env


def render():
    df = get_energy_mix_for_all_scenarios()
    three = get_energy_mix_by_scenario(df, 'three')
    four = get_energy_mix_by_scenario(df, 'four')
    five = get_energy_mix_by_scenario(df, 'five')
    nonfossil, _ = get_nonfossil(include_bau=True, end_factor=15)
    template = env.get_template('viz/national_energy_mix.html')
    script, div = components(
        dict(three=three, four=four, five=five, nonfossil=nonfossil),
        wrap_plot_info=False
    )
    return template.render(plot_script=script, plot_div=div)
