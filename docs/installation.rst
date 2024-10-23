Installation
============

The following instructions will allow you to install PyIRTAM.

Prerequisites
-------------

PyIRTAM uses the Python modules included in the list below. This module
officially supports Python 3.9+.

1. numpy
2. PyIRI
3. requests


Installation Option 1
---------------------
1. Make sure that your version of pip is same as python.
E.g., if you are using Python3, you also should use pip3.
To check that, type in your terminal::

        which python3


and::

        which pip3

The output directories must be the same.

2. Once you made sure that your pip connects to the correct python,
use the following command in your terminal::

        pip install PyIRTAM

This installation will take care of all the dependencies.
For example, PyIRTAM uses PyIRI module and Numpy module.

Installation Option 2
---------------------

1. Clone the git repository
::


   git clone https://github.com/victoriyaforsythe/PyIRTAM.git


2. Install PyIRTAM:
   Change directories into the repository folder and build the project.
   There are a few ways you can do this:

   A. Install on the system (root privileges required)::


        sudo pip install .

   B. Install at the user level::


        pip install --user .

   C. Install with the intent to change the code::


        pip install --user -e .

Optional Requirements
---------------------

To run the test suite and build the documentation locally, you also need the
following Python packages.

.. extras-require:: test
    :pyproject:

.. extras-require:: doc
    :pyproject:
