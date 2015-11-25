# The render functions here are used by the pelican reader to assemble the plot


def render_co2_by_scenario():
    from .co2_by_scenario import render
    return render()


def render_air_pollution():
    from .air_pollution import render
    return render()


def render_co2_by_province():
    from .co2_by_province import render
    return render()


def render_health_impacts_by_province():
    from .health_impacts_by_province import render
    return render()


def render_energy_mix():
    from .energy_mix import render
    return render()


def render_comparison_provincial():
    from .comparison_provincial import render
    return render()


def render_comparison_national():
    from .comparison_national import render
    return render()


def render_comparison_national_lo_growth():
    from .comparison_national_lo_growth import render
    return render()
