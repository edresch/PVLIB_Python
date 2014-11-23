PVLIB_Python
============

The PV_LIB Toolbox provides a set of well-documented functions for simulating the performance of photovoltaic energy systems. The toolbox was developed at Sandia National Laboratories and it implements many of the models and methods developed at the Labs.


Compatibility
=============

PV_LIB is currently compatible with python 2.7.X

Getting Started
===============

After cloning the directory onto your local computer, the best place to start is running the example ipython notebook files (.ipynb)

To start a notebook session, enter the local directory of the PV_LIB library and run 

     ipython notebook --pylab

Development
===========

The PV_LIB package is functional as it is currently implemented (though, if you run into a issue, please report it through the issues tracker!)

However, the pacakge is still under development, and an upgraded version is available under the 'develop' branch of the repository. This version includes the following changes: 

* Remove ``pvl_`` from module names.
* Consolidation of similar modules. For example, functions from ``pvl_clearsky_ineichen.py`` and ``pvl_clearsky_haurwitz.py`` have been consolidated into ``clearsky.py``. 
* Added ``/pvlib/data`` for lookup tables
* Return one DataFrame instead of a tuple of DataFrames
* Upgraded handling of timezones and location information
* Expanded unit testing
* Add PyEphem option to solar position calculations. 

This new version increases the usability of the system, and shifts it towards a more "pythonic" implementation. 


Notebooks to run
---------------------

*  /tutorial/Tutorial.ipynb for an introduction to the overall functionality 

* /pvlib/Test_scripts_1.ipynb an example of a complete workflow

* /pvlib/TS_2_irradiance_functions.ipynb an example of implementing the included irradiance translation functions
 
