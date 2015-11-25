# The render functions here are used by the pelican reader to assemble the plot


def render_air_pollution():
    from .national_air_pollution import render
    return render()


def render_energy_mix():
    from .national_energy_mix import render
    return render()


def render_comparison_national():
    from .national_comparison import render
    return render()


def render_comparison_national_lo_growth():
    from .national_comparison_economic import render
    return render()


def render_co2_by_province():
    from .by_province_co2 import render
    return render()


def render_health_impacts_by_province():
    from .by_province_health_impacts import render
    return render()


def render_comparison_provincial():
    from .by_province_comparison import render
    return render()
