# -*- coding: utf-8 -*- #
from .__utils import env

from os.path import join

def render():
    template = env.get_template('home_page.html')
    pages = [
        {
            "title": "Air pollution",
            "link": "air-pollution",
            "text": "China has a unique opportunity to clean up CO₂ and local air pollution at the same time."
        },
        {
            "title": "Energy mix",
            "link": "energy-mix",
            "text": "China's target of 20% of energy from non-fossil sources (wind, solar, hydro, and nuclear power) is met in 2030 in the 4% scenario."
        },
        {
            "title": "National comparison",
            "link": "national-comparison",
            "text": "To reach a CO₂ emissions peak by 2030 under baseline economic assumptions, China’s CO₂ intensity will need to fall between 4%-5%/year."
        },
        {
            "title": "Economic growth",
            "link": "economic-growth",
            "text": "Slower economic growth means an earlier CO₂ emissions peak, less expansion of non-fossil energy"
        },
        {
            "title": "CO₂ by province",
            "link": "co2-by-province",
            "text": "The effects of policy vary widely across China’s provinces, consistent with diverse features of provincial energy systems and economies."
        },
        {
            "title": "Health impacts by province",
            "link": "health-impacts-by-province",
            "text": "Combining the spatial distribution of population with projections of air quality provide insight where the health consequences will be greatest."
        },
        {
            "title": "Provincial comparison",
            "link": "provincial-comparison",
            "text": "The impacts of policy on provinces can be traced to differences in population, per-capita income, and reliance on coal"
        }
    ]
    return template.render(page_index=pages)
