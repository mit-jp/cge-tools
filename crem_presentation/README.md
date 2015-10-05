# Create a conda environment, and install the necessary packages

 $ conda create -n crem_presentation --file conda-requirements.txt
 $ source activate crem_presentation

# Add the site generator dependencies

 $ pip install pelican
 $ pip install markdown

# Work with grunt to build the site

Get node, then install node packages

 $ conda install node
 $ cd pelican
 $ npm install

You should have a new folder inside your pelican directory called `node_modules`

To use the site locally, from the pelican directory:

 $ ./node_modules/grunt-cli/bin/grunt serve

Any changes you make to content, will cause the site to be automatically rebuilt and 
the page will refresh (may take a minute)

# To deploy

First check that you have a file `private_settings.py` and that it has your correct SITEURL set.

 $ ./node_modules/grunt-cli/bin/grunt deploy

This will create a fresh build in the `output` directory which can be copied to your server, for example:

 $ scp -r output/* user@my.host.com:/path/to/site/

====================================
Unlikely to need to do the following, but documented just in case

# To manipulate the shape files

 $ conda install -c https://conda.anaconda.org/osgeo gdal

Then copy across libhdf5.10.dylib and libhdf5_hl.10.dylib into your
envs lib directory. These can be found in an that has `conda install hdf5`.


