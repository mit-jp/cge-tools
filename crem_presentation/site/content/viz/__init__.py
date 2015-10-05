# The render functions here are used by the pelican reader to assemble the plot

def render_co2_by_scenario():
    from .co2_by_scenario import render
    return render()
