#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='CGE Tools',
      version='0.1',
      author='China Energy & Climate Project',
      author_email='cecp@mit.edu',
      description='Analysis and visualization codes for CGE models and related data.',
      install_requires=['bokeh >= 0.9', 'xray >= 0.4'],
      url='https://github.com/mit-jp/cge-tools',
      packages=find_packages(),
      )

