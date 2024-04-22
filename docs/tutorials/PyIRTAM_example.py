#!/usr/bin/env python
# --------------------------------------------------------
# Distribution statement A. Approved for public release.
# Distribution is unlimited.
# This work was supported by the Office of Naval Research.
# --------------------------------------------------------

import datetime as dt
import numpy as np
import PyIRI
import PyIRI.main_library as ml
import PyIRTAM
import PyIRTAM.lib as il
import time


# To record how long it takes to run this script get the start time
st = time.time()

# Create 5x5 horizontal grid:
alon, alat, alon_2d, alat_2d = ml.set_geo_grid(5, 5)

# Create vertical grid:
aalt = np.arange(100, 700, 10)

# Create 15-min resolution time array:
aUT = np.arange(0, 24, 0.25)

# Day of Interest:
year = 2022
month = 1
day = 1
dtime = dt.datetime(year, month, day)

# Specify F10.7:
F107 = 79.9

# Directory on your machine where IRTAM coefficients live
irtam_dir = '/Users/vmakarevich/Documents/Science_VF2/PyIRTAM/IRTAM/'

# Directory on your machine where you want to save plots
save_plot_dir = '/Users/vmakarevich/Documents/Science_VF2/PyIRI_Test/'

# First, determine the standard PyIRI parameters for the day of interest
# It is better to do it in the beginning (outside the time loop),
# so that PyIRI is called only once for the whole day.
ccir_or_ursi = 1  # 0 = CCIR, 1 = URSI
f2_b, f1_b, e_b, es_b, sun, mag, edp_b = ml.IRI_density_1day(year,
                                                             month,
                                                             day,
                                                             aUT,
                                                             alon,
                                                             alat,
                                                             aalt,
                                                             F107,
                                                             PyIRI.coeff_dir,
                                                             ccir_or_ursi)

print('PyIRI run for the day is completed. Starting IRTAM part:')

for it in range(0, aUT.size):
    
    # Dtime for one time frame
    hour = int(np.fix(aUT[it]))
    minute = int((aUT[it] - hour) * 60.)
    dtime = dt.datetime(year, month, day, hour, minute, 0)
    
    print('Working with time frame: ', dtime)

    # THIS IS THE MAIN FUNCTION TO CALL FOR IRTAM:
    F2, F1, E, Es, EDP = il.call_IRTAM_PyIRI(aUT,
                                             dtime,
                                             alon,
                                             alat,
                                             aalt,
                                             f2_b,
                                             f1_b,
                                             e_b,
                                             es_b,
                                             mag['modip'],
                                             aUT[it],
                                             PyIRI.coeff_dir,
                                             irtam_dir)

    # Save the results here by adding them to the array or
    # making a pickle or .nc file

# Get the end time of the script run and the execution time
et = time.time()
elapsed_time = et - st
print('Execution time:', elapsed_time, 'seconds')