from os.path import dirname, join

from bokeh.embed import file_html
from bokeh.models import Callback, ColumnDataSource, HoverTool, Patches, Plot, \
    Range1d, Select, TapTool
from bokeh import palettes
from bokeh.plotting import vplot
from bokeh.resources import Resources
from IPython.display import display_html
from jinja2 import Template
import pandas as pd
import numpy as np

from .constants import PLOT_FORMATS


__all__ = ['color_data', 'live_map',]


DATA_DIR = join(dirname(__file__), 'data')


def get_map_df():
    map_data = pd.read_json(join(DATA_DIR, 'province_map_data.json'))

    def convert_none_to_np_nan(r):
        r['xs'] = np.array(r['xs'], dtype=float)
        r['ys'] = np.array(r['ys'], dtype=float)
        return r

    map_data = map_data.apply(convert_none_to_np_nan, axis=1)
    return map_data


def color_data(data, columns_to_colorize, data_min=None, data_max=None,
               palette=palettes.Blues9):
    # data - the data frame which you are adding colored values to
    # columns_to_colorize - a list of strings which select the columns

    if data_min is None:
        data_min = np.floor(np.amin(data[columns_to_colorize].values))

    if data_max is None:
        data_max = np.ceil(np.amax(data[columns_to_colorize].values))

    data_range = data_max - data_min
    bin_factor = data_range / len(palette)

    def _get_color(value, palette):
        return palette[int((value - data_min) / bin_factor)]

    for column_name in columns_to_colorize:
        color_name = '%s_color' % column_name
        data[color_name] = data['%s' % column_name].apply(_get_color,
                                                          args=([palette]))
    return data, (data_min, data_max)


def build_map(data, variables, years=None, plot_width=800,
                         x_range=[70, 140], y_range=[10, 60], title=""):
    #aspect_ratio = (x_range[1] - x_range[0]) / (y_range[1] - y_range[0])
    #plot_height = int(plot_width / aspect_ratio)
    plot_height = plot_width
    x_range = Range1d(x_range[0], x_range[1])
    y_range = Range1d(y_range[0], y_range[1])

    plot = Plot(
        x_range=x_range,
        y_range=y_range,
        title=title,
        plot_width=plot_width,
        plot_height=plot_height,
        **PLOT_FORMATS)

    if years is None:
        tt_year = '—'
        tt_var = variables[0]
        color_column = '{}_color'.format(variables[0])
    else:
        tt_year = '@active_year'
        tt_var = 'active_value'
        color_column = 'active_color'
    tooltip = """<span class='tooltip-text year'>{}</span>
        <span class='tooltip-text country'>@alpha @name_zh @name_en</span>
        <span class='tooltip-text value'>@{}</span>""".format(tt_year, tt_var)
    plot.add_tools(HoverTool(tooltips=tooltip))

    source = ColumnDataSource(data)

    countries = Patches(
        xs='xs',
        ys='ys',
        fill_color=color_column,
        line_color='#000000'
        )

    renderer = plot.add_glyph(source, countries)

    if years is None:
        return plot

    callback = Callback(code="""
        var year = select.get('value');
        var data = source.get('data');
        var i = %d;
        data['active_color'] = data[year + '_color'];
        data['active_value'] = data[year];
        while (--i >= 0) {
            // Instead of doing this I'd like to
            // be able to change the hover tool
            data['active_year'][i] = year;
        }
        source.trigger('change');
        """ % len(years))
    select = Select(title="Year", options=years, value=years[-1],
                    callback=callback)
    callback.args = {
        'select': select,
        'source': source
        }

    layout = vplot(select, plot)

    return layout


def live_map(gdx_file, variable, verbose=False):
    # Read the indicated variable(s) from the GDX file
    data = gdx_file.extract(variable)
    # Truncate unused years
    if 't' in data.coords:
        t_max = int(gdx_file.extract('t_max'))
        years = list(filter(lambda t: int(t) <= t_max, gdx_file.set('t')))
        columns = years
        data = data.sel(t=years)
    else:
        years = None
        columns = [variable]
    # Determine the coordinate containing region data
    region = 'r' if 'r' in data.coords else 'rs'
    if region == 'rs':
        data = data.sel(rs=gdx_file.set('r'))
    if 't' in data.coords:
        data = data.to_dataframe().T.stack(region)
        data.index = data.index.droplevel(0)
    else:
        data = data.to_dataframe()

    # Load map coordinates, merge, and colorize
    map_data = pd.read_hdf(join(DATA_DIR, 'province_map_data.hdf'), 'df')
    if verbose:
        print(data)
    all_data = map_data.merge(data, left_on='alpha', right_index=True)
    colored_data, data_range = color_data(all_data, columns)

    if years is not None:
        colored_data['active_year'] = t_max
        colored_data['active_value'] = colored_data[str(t_max)]
        colored_data['active_color'] = colored_data['%s_color' % t_max]

    # Plot title: description of the variable to be plotted
    TITLE = gdx_file[variable].attrs['_gdx_description']

    # Build the map
    map_box = build_map(colored_data, columns, years)

    # Output the map
    # Open our custom HTML template
    with open(join(DATA_DIR, 'map_template.jinja'), 'r') as f:
        template = Template(f.read())

    resources = Resources(mode='inline')
    # Update these to change the text
    template_variables = {
        'title': TITLE,
        'narrative': 'Data range: {}–{}'.format(data_range[0], data_range[1]),
        'tooltip_css': open(join(DATA_DIR, 'tooltip.css')).read(),
        'bokeh_min_js': resources.js_raw[0],
        }

    # Use inline resources, render the html and open
    html = file_html(map_box, resources, TITLE, template=template,
                     template_variables=template_variables)
    display_html(html, raw=True)
