These install instructions work on OSX (and almost certainly linux) but don't 
work exactly on windows. In particular, can't install the environment
from the conda-requirements file and you need to install nodejs manually.
Consult a helper to get going on windows.


# Create a conda environment, and install the necessary packages

  $ conda create -n crem_presentation --file conda-requirements.txt
  $ source activate crem_presentation

# Add the site generator dependencies

  $ pip install pelican markdown

# Work with grunt to build the site

Install node packages

  $ cd site
  $ npm install

You should have a new folder inside your site directory called `node_modules`

To use the site locally, from the site directory:

  $ ./node_modules/grunt-cli/bin/grunt serve

Any changes you make to content, will cause the site to be automatically rebuilt and 
the page will refresh (may take a minute)

# To deploy

First check that you have a file `private_settings.py` and that it has your correct SITEURL set.

  $ ./node_modules/grunt-cli/bin/grunt deploy

This will create a fresh build in the `output` directory which can be copied to your server, for example:

  $ scp -r output/* user@my.host.com:/path/to/site/

# To run the notebooks under working

It is best to run `ipython notebook` from the parent directory of `crem_presentation`.

====================================
Unlikely to need to do the following, but documented just in case

# Build conda environment not from requirements file
  $ conda install bokeh ipython-notebook nodejs pytables matplotlib


# To manipulate the shape files

  $ conda install -c https://conda.anaconda.org/osgeo gdal

Then copy across libhdf5.10.dylib and libhdf5_hl.10.dylib into your
envs lib directory. These can be found in an that has `conda install hdf5`.


