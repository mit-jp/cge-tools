# The render functions here are used by the pelican reader to assemble the plot


def render_co2_by_scenario():
    from .co2_by_scenario import render
    return render()


def render_air_pollution_1():
    from .air_pollution import render_1
    return render_1()


def render_air_pollution_2():
    from .air_pollution import render_2
    return render_2()
