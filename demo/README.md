## Interactive maps

The notebooks in this directory allow you to map data that is:
* by province
* by province & time

onto an existing province map of china.

The plotting is done using [Bokeh](http://bokeh.pydata.org/)

### Installation

#### Download copy of cge-tools via zip

https://github.com/mit-jp/cge-tools/archive/master.zip

Unzip the folder and go into the interactive_map directory.

#### Python environment

If you are using the anaconda distribution of python (http://continuum.io/downloads) 
it should contain Bokeh & IPython notebook already and these notebooks should just work.

If you are not, you will need to install bokeh (Note that Bokeh v0.10+ is expected), and its dependencies, via conda or pip:

    $ pip install bokeh "ipython[notebook]" pandas
    or
    $ conda install bokeh ipython-notebook pandas

To use hdf, install pytables:

    $ conda install pandas pytables
