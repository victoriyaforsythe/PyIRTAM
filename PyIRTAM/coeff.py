#!/usr/bin/env python
# --------------------------------------------------------
"""This module contains functions to obtain and update the IRTAM coefficients.

"""
import os
import requests

import PyIRTAM


def download_irtam_coeffs(dtime, param, irtam_dir='', use_subdirs=True,
                          overwrite=False):
    """Retrieve the IRTAM coefficients from the UMass Lowell GIRO Data Center.

    Parameters
    ----------
    dtime : dt.datetime
        Date and time for the desired coefficents
    param : str
        Coefficient parameter to retrieve. Expects one of: 'foF2', 'hmF2', 'B0',
        and 'B1'
    irtam_dir : str
        Directory for IRTAM coefficients, or '' to use package directory.
        (default='')
    use_subdirs : bool
        If True, adds YYYY/MMDD subdirectories to the filename path, if False
        assumes that the entire path to the coefficient directory is provided
        by `irtam_dir` (default=True)
    overwrite : bool
        Allow overwriting of existing parameter files if True (default=False)

    Returns
    -------
    dstat : bool
        Download status: True if file was downloaded, False if not
    fstat : bool
        File status: True if parameter coefficient file exists, False if not
    msg : str
        Potential message with more details about status flags, empty if both
        are True

    Notes
    -----
    LGDC claims to also support 'VTEC', 'MUF3000', 'TAU', but tests for these
    paramaters failed

    """
    PyIRTAM.logger.info('Downloading coefficients from GAMBIT for: {:}'.format(
        param))

    # Initalize output
    dstat = False
    fstat = False
    msg = ''

    # If no directory is provided, use the package default
    if irtam_dir == '':
        irtam_dir = PyIRTAM.irtam_coeff_dir

    # Determine the appropriate output filename
    param_file = get_irtam_param_filename(dtime, param, irtam_dir, use_subdirs)
    PyIRTAM.logger.info('Saved as: {:}'.format(param_file))

    # Ensure the desired output directory exists
    dir_name = os.path.dirname(param_file)

    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)
        PyIRTAM.logger.info('Created coefficient directory: {:}'.format(
            dir_name))

    # Test to see if the file exists already, if overwriting is not desired
    if os.path.isfile(param_file):
        fstat = True
        msg = 'IRTAM parameter coefficient file exists: {:}'.format(param_file)
        if not overwrite:
            PyIRTAM.logger.warning(msg)
            return dstat, fstat, msg
        else:
            msg = "".join(["Overwriting ", msg])

    # Construct the query
    base_url = "https://lgdc.uml.edu/rix/gambit-coeffs"
    url = "".join([base_url, "?charName=", param, "&time=", dtime.strftime(
        "%Y.%m.%dT%H:%M:%S")])

    # Download the webpage
    req = requests.get(url)

    # Test to see if the data was retrieved successfully
    if req.text.find('START_HEADER') < 0:
        # No data was retrieved
        msg = ''.join([msg, '' if len(msg) == 0 else '\n',
                       'Bad IRTAM coefficient query: ', url,
                       '\nRemote message: ', req.text])
        PyIRTAM.logger.warning(msg)
        return dstat, fstat, msg

    # Write the new coefficients to the desired output file
    dstat = True
    fstat = True
    with open(param_file, 'w') as fout:
        fout.write(req.text)

    if len(msg) > 0:
        PyIRTAM.logger.info(msg)

    return dstat, fstat, msg


def get_irtam_param_filename(dtime, param, irtam_dir='', use_subdirs=True):
    """Determine the filename for the desired IRTAM coefficients.

    Parameters
    ----------
    dtime : dt.datetime
        Date and time for the desired coefficents
    param : str
        Coefficient parameter to retrieve. Expects one of: 'foF2', 'hmF2', 'B0',
        and 'B1'
    irtam_dir : str
        Directory for IRTAM coefficients, or '' to use package directory.
        (default='')
    use_subdirs : bool
        If True, adds YYYY/MMDD subdirectories to the filename path, if False
        assumes that the entire path to the coefficient directory is provided
        by `irtam_dir` (default=True)

    Returns
    -------
    filename : str
        IRTAM coefficient filename with full directory path

    """
    # If no directory is provided, use the package default
    if irtam_dir == '':
        irtam_dir = PyIRTAM.irtam_coeff_dir

    # Construct the desired filename
    time_str = ''.join([dtime.strftime('%Y%m%d'), '_', dtime.strftime('%H%M%S'),
                        '.ASC'])

    # Update the parameter name
    if param in ['B0', 'B1']:
        param_name = ''.join([param, 'in'])
    else:
        param_name = param

    # Construct file with or without year and month-day subdirectories
    if use_subdirs:
        filename = os.path.join(irtam_dir, dtime.strftime('%Y'),
                                dtime.strftime('%m%d'),
                                '_'.join(['IRTAM', param_name, 'COEFFS',
                                          time_str]))
    else:
        filename = os.path.join(irtam_dir, '_'.join(['IRTAM', param_name,
                                                     'COEFFS', time_str]))

    return filename
