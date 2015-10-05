# Create a conda environment, and install the necessary packages

 $ conda create -n crem_presentation --file conda-requirements.txt
 $ source activate crem_presentation

# Add the site generator

 $ pip install pelican
 $ pip install markdown


# To manipulate the shape files

 $ conda install -c https://conda.anaconda.org/osgeo gdal

Then copy across libhdf5.10.dylib and libhdf5_hl.10.dylib into your
envs lib directory. These can be found in an that has `conda install hdf5`.


