Example 1: Daily Ionospheric Parameters
=======================================

PyIRTAM can calculate daily ionospheric parameters for the user provided
IRTAM coefficients and grid. The estimation of the parameters occurs
simultaneously at all grid points and for all desired diurnal time frames. 

1. Import libraries:

::

   import datetime as dt
   import numpy as np
   import PyIRI
   import PyIRTAM
   import PyIRI.main_library as ml
   import PyIRI.plotting as plot

2. Specify a year, a month, and a day:

::


   year = 2022
   month = 1
   day = 1
   dtime = dt.datetime(year, month, day)

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
   
7. Specify a directory on your machine where IRTAM coefficients live. If you
   don't want to specify this, PyIRTAM will create a directory within the
   package as a default. This location can be found through the variable
   ``PyIRTAM.irtam_coeff_dir``:

::

   irtam_dir = '~/Data/IRTAM_Coeffs/'  # Directory need not exist

8. Download the IRTAM coefficients from the UMass Lowell data base. By default,
   these will be stored in subdirectories that separate data by year and
   month-day:

::

   for param in ['B0', 'B1', 'hmF2', 'foF2']:
       PyIRTAM.coeff.download_irtam_coeffs(dtime, param, irtam_dir=irtam_dir)

9. Run PyIRTAM:

::

   (f2_iri, f1_iri, e_iri, es_iri, sun, mag, edp_iri, f2_irtam, f1_irtam,
    e_irtam, es_irtam, edp_irtam) = PyIRTAM.run_PyIRTAM(year, month, day, aUT,
                                                        alon, alat, aalt, F107,
                                                        irtam_dir=irtam_dir)

10. Plot results and saved at given location, suggestion provided:

::

   save_plot_dir = '~/Plots/IRTAM/'  # Directory must exist
   
   UT_show = 10
   plot.PyIRI_plot_NmF2(f2, ahr, alon, alat, alon_2d, alat_2d, sun,
   
   plot.PyIRI_plot_NmF2(f2_iri, aUT, alon, alat, alon_2d, alat_2d, sun,
                        UT_show, save_plot_dir, plot_name='PyIRI_NmF2.pdf')

   plot.PyIRI_plot_NmF2(f2_irtam, aUT, alon, alat, alon_2d, alat_2d, sun,
                        UT_show, save_plot_dir, plot_name='PyIRTAM_NmF2.pdf')

.. image:: Figs/PyIRI_NmF2.pdf
    :width: 600px
    :align: center
    :alt: Global distribution of NmF2 from PyIRI.

.. image:: Figs/PyIRTAM_NmF2.pdf
    :width: 600px
    :align: center
    :alt: Global distribution of NmF2 from PyIRTAM.

   plot.PyIRI_plot_hmF2(f2_iri, aUT, alon, alat, alon_2d, alat_2d, sun,
                        UT_show, save_plot_dir, plot_name='PyIRI_hmF2.pdf')

   plot.PyIRI_plot_hmF2(f2_irtam, aUT, alon, alat, alon_2d, alat_2d, sun,
                        UT_show, save_plot_dir, plot_name='PyIRTAM_hmF2.pdf')

.. image:: Figs/PyIRI_hmF2.pdf
    :width: 600px
    :align: center
    :alt: Global distribution of hmF2 from PyIRI.

.. image:: Figs/PyIRTAM_hmF2.pdf
    :width: 600px
    :align: center
    :alt: Global distribution of hmF2 from PyIRTAM.

11. Plot density time series for PyIRI and PyIRTAM at specified location:

::

   lon_plot = 0
   lat_plot = 0
   
   plot.PyIRI_plot_1location_diurnal_density(edp_iri, alon, alat, lon_plot,
                                             lat_plot, aalt, aUT, save_plot_dir,
                                             plot_name='PyIRI_EDP_diurnal.pdf')

   plot.PyIRI_plot_1location_diurnal_density(
       edp_irtam, alon, alat, lon_plot, lat_plot, aalt, aUT, save_plot_dir,
       plot_name='PyIRTAM_EDP_diurnal.pdf')

.. image:: Figs/PyIRI_diurnal.pdf
    :width: 600px
    :align: center
    :alt: Diurnal distribution of density from PyIRI.

.. image:: Figs/PyIRTAM_diurnal.pdf
    :width: 600px
    :align: center
    :alt: Diurnal distribution of density from PyIRTAM.
