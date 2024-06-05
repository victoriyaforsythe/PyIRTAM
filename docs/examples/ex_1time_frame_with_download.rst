Example 2: Download coefficients and run for 1-time frame
=========================================================

PyIRTAM can download coefficients and calculate parameters and density for 
a particular time frame. The estimation of the parameters occurs
simultaneously at all grid points. 

1. Import libraries:

::

   import datetime as dt
   import numpy as np
   import PyIRI.main_library as ml
   import PyIRTAM

2. Specify a year, a month, and a day:

::


   year = 2020
   month = 1
   day = 1
   hour = 2
   minute = 15
   # Specify array for decimal hour
   ahr = np.array([hour + minute / 60.])
   dtime = dt.datetime(year, month, day, hour, minute, 0)

3. Specify solar flux index F10.7 in SFU:

::


   f107 = 90.8

4. Create any horizontal grid (regular or irregular, global or regional).
   The grid arrays (alon and alat) should be flattened to be 1-D arrays. 
   This is an example of a regular global grid:

::

   dlon = 5
   dlat = 5
   # Create 5x5 horizontal grid:
   alon, alat, alon_2d, alat_2d = ml.set_geo_grid(dlon, dlat)

5. Create any temporal array expressed in decimal hours (regular or irregular).
   IRTAM coefficients have 15-min resolution. For max resolution use 15 min.
   For this example we use regularly spaced time array:

::

   hr_res = 0.25
   ahr = np.arange(0, 24, hr_res)

6. Create height array. It can be regular or irregular.
   Here is an example for regularly spaced array:

::

   alt_res = 10
   alt_min = 90
   alt_max = 700
   aalt = np.arange(alt_min, alt_max, alt_res)
   
7. Run PyIRTAM for the selected time frame. If irtam_dir='' in the inputs,
   the coefficients will be downloaded.

::

   (f2_iri, f1_iri, e_iri, es_iri, sun, mag, edp_iri, f2_irtam, f1_irtam,
e_irtam, es_irtam, edp_irtam) = PyIRTAM.run_PyIRTAM(year, month, day, ahr,
                                                    alon, alat, aalt, f107,
                                                    irtam_dir='')
