#!/usr/bin/env python
# --------------------------------------------------------
# Distribution statement A. Approved for public release.
# Distribution is unlimited.
# This work was supported by the Office of Naval Research.
# --------------------------------------------------------
"""This library contains components for PyIRTAM software.

References
----------
Forsythe et al. (2023), PyIRI: Whole-Globe Approach to the
International Reference Ionosphere Modeling Implemented in Python,
Space Weather, ESS Open Archive, September 28, 2023.

Bilitza et al. (2022), The International Reference Ionosphere
model: A review and description of an ionospheric benchmark, Reviews
of Geophysics, 60.

"""

import datetime as dt
import numpy as np
import os

import PyIRI
import PyIRI.main_library as ml


def IRTAM_density(dtime, alon, alat, modip, TOV, coeff_dir, irtam_dir):
    """Output ionospheric parameters from daily set of IRTAM coefficients.

    Parameters
    ----------
    dtime : object
        Datetime Python object.
    alon : array-like
        Flattened array of geographic longitudes in degrees.
        Must be Numpy array
        of any size [N_G].
    alat : array-like
        Flattened array of geographic latitudes in degrees.
        Must be Numpy array
        of any size [N_G].
    modip : array-like
        Modified dip angle in degrees.
    TOV : float
        Time of Validity for IRtAM coefficients (use 24 if unknown).
    coeff_dir : str
        Place where model coefficients are located.
    irtam_dir : str
        Place where IRTAM coefficients are located (user provided).

    Returns
    -------
    F2 : dict
        'fo' is critical frequency of F2 region in MHz.
        'hm' is height of the F2 peak in km.
        'B0' is bottom thickness parameter of the F2 region in km.
        'B1' is bottom thickness parameter of the F2 region in km.
        Shape [N_T, N_G].

    Notes
    -----
    This function returns ionospheric parameters and 3-D electron density
    for a given time using IRTAM coefficients for that time frame.

    References
    ----------
    Galkin et al. (2015), GAMBIT Database and Explorer for Real-Time
    IRI Maps of F2 Layer Peak Height and Density, IES. url:
    https://ies2015.bc.edu/wp-content/uploads/2015/05/061-Galkin-Paper.pdf

    Forsythe et al. (2023), PyIRI: Whole-Globe Approach to the
    International Reference Ionosphere Modeling Implemented in Python,
    Space Weather.

    """
    # ------------------------------------------------------------------------
    # Calculate geographic Jones and Gallet (JG) functions F_G for the given
    # grid and corresponding map of modip angles
    G_IRTAM = IRTAM_set_gl_G(alon, alat, modip)

    # ------------------------------------------------------------------------
    # Calculate diurnal Fourier functions F_D for the given time array aUT
    # create time array that matches IRTAM files (15 min)

    # Diurnal function for a single time frame (nat all, like in PyIRI)
    aUT = np.array([dtime.hour + dtime.minute / 60.])
    D_IRTAM = IRTAM_diurnal_functions(aUT, TOV)

    # ------------------------------------------------------------------------
    # Read IRTAM coefficients and form matrix U
    F_B0, F_B1, F_f0F2, F_hmF2 = IRTAM_read_coeff(dtime, irtam_dir)

    # ------------------------------------------------------------------------
    # Multiply matrices (F_D U)F_G
    B0, B1, foF2, hmF2 = IRTAM_gamma(G_IRTAM, D_IRTAM,
                                     F_B0, F_B1, F_f0F2, F_hmF2)

    # Limit B1 values (same as in IRI) to prevent ugly thin profiles:
    B1 = np.clip(B1, 1., 6.)
    B0 = np.clip(B0, 1., 350.)
    # ------------------------------------------------------------------------
    # Add all parameters to dictionaries:
    F2 = {'B0': B0,
          'B1': B1,
          'fo': foF2,
          'hm': hmF2}

    return F2


def IRTAM_set_gl_G(alon, alat, modip):
    """Calculate global functions.

    Parameters
    ----------
    alon : array-like
        Flattened array of geographic longitudes in degrees.
    alat : array-like
        Flattened array of geographic latitudes in degrees.
    modip : array-like
        Modified dip angle in degrees.

    Returns
    -------
    G : array-like
        Global functions for IRTAM (same as for CCIR foF2).

    Notes
    -----
    This function sets Geographic Coordinate Functions G_k(position) page
    # 18 of Jones & Graham 1965 for F0F2, M3000, and Es coefficients

    References
    ----------
    Forsythe et al. (2023), PyIRI: Whole-Globe Approach to the
    International Reference Ionosphere Modeling Implemented in Python,
    Space Weather.

    Galkin et al. (2015), GAMBIT Database and Explorer for Real-Time
    IRI Maps of F2 Layer Peak Height and Density, IES. url:
    https://ies2015.bc.edu/wp-content/uploads/2015/05/061-Galkin-Paper.pdf

    Jones, W. B., & Gallet, R. M. (1965). Representation of diurnal
    and geographic variations of ionospheric data by numerical methods,
    control of instability, ITU Telecommunication Journal , 32 (1), 18–28.

    """
    coef = ml.highest_power_of_extension()

    G = ml.set_global_functions(coef['QM']['F0F2'],
                                coef['nk']['F0F2'],
                                alon, alat, modip)

    return G


def IRTAM_diurnal_functions(time_array, TOV):
    """Set diurnal functions for F2, M3000, and Es.

    Parameters
    ----------
    time_array : array-like
        Array of UTs in hours.

    Returns
    -------
    D : array-like
        Diurnal functions for IRTAM.

    Notes
    -----
    This function calculates diurnal functions for IRTAM
    coefficients

    References
    ----------
    Galkin et al. (2015), GAMBIT Database and Explorer for Real-Time
    IRI Maps of F2 Layer Peak Height and Density, IES. url:
    https://ies2015.bc.edu/wp-content/uploads/2015/05/061-Galkin-Paper.pdf

    Forsythe et al. (2023), PyIRI: Whole-Globe Approach to the
    International Reference Ionosphere Modeling Implemented in Python,
    Space Weather.

    Jones, W. B., Graham, R. P., & Leftin, M. (1966). Advances
    in ionospheric mapping by numerical methods.

    """
    # nj is the highest order of the expansion
    coef = IRTAM_highest_power_of_extension()
    time_array = time_array
    # First find CCIR-like diurnal functions
    D_CCIR = ml.set_diurnal_functions(coef['nj']['F0F2'], time_array)

    # Then we need to reorder them to insert additional term for IRTAM
    D = np.zeros((coef['nj']['IRTAM'], time_array.size))
    D[0, :] = D_CCIR[0, :]
    D[1, :] = (time_array - TOV) * 60. + 720.
    D[2:, :] = D_CCIR[1:, :]

    # Transpose array so that multiplication can be done later
    D = np.transpose(D)

    return D


def IRTAM_read_coeff(dtime, coeff_dir):
    """Read coefficients from IRTAM.

    Parameters
    ----------
    dtime : int
        Month.
    coeff_dir : str
        Place where the coefficient files are.

    Returns
    -------
    F_B0_IRTAM : array-like
        IRTAM coefficients for B0 thickness.
    F_B1_IRTAM : array-like
        IRTAM coefficients for B1 thickness.
    F_fof2_IRTAM : array-like
        IRTAM coefficients for F2 frequency.
    F_hmf2_IRTAM : array-like
        IRTAM coefficients for F2 peak height.

    Notes
    -----
    This function reads U_jk coefficients (from IRTAM and Es maps).
    Acknowledgement for Es coefficients:
    Mrs. Estelle D. Powell and Mrs. Gladys I. Waggoner in supervising the
    collection, keypunching and processing of the foEs data.
    This work was sponsored by U.S. Navy as part of the SS-267 program.
    The final development work and production of the foEs maps was supported
    by the U.S Information Agency.
    Acknowledgments to Doug Drob (NRL) for giving me these coefficients.

    References
    ----------
    Galkin et al. (2015), GAMBIT Database and Explorer for Real-Time
    IRI Maps of F2 Layer Peak Height and Density, IES. url:
    https://ies2015.bc.edu/wp-content/uploads/2015/05/061-Galkin-Paper.pdf

    Forsythe et al. (2023), PyIRI: Whole-Globe Approach to the
    International Reference Ionosphere Modeling Implemented in Python,
    Space Weather.

    Jones, W. B., Graham, R. P., & Leftin, M. (1966). Advances
    in ionospheric mapping 476 by numerical methods.

    """
    # IRTAM coefficients:
    # the file has first 988 numbers in same format as CCIR
    # followed by 76 coefficients for the additional diurnal term
    time_str = ''.join([dtime.strftime('%Y%m%d'), '_', dtime.strftime('%H%M%S'),
                        '.ASC'])

    # B0
    file_B0 = os.path.join(coeff_dir, dtime.strftime('%Y'),
                           dtime.strftime('%m%d'),
                           ('IRTAM_B0in_COEFFS_' + time_str))

    F_B0 = IRTAM_read_files(file_B0)

    # B1
    file_B1 = os.path.join(coeff_dir, dtime.strftime('%Y'),
                           dtime.strftime('%m%d'),
                           ('IRTAM_B1in_COEFFS_' + time_str))

    F_B1 = IRTAM_read_files(file_B1)

    # f0F2
    file_f0F2 = os.path.join(coeff_dir, dtime.strftime('%Y'),
                             dtime.strftime('%m%d'),
                             ('IRTAM_foF2_COEFFS_' + time_str))

    F_f0F2 = IRTAM_read_files(file_f0F2)

    # hmF2
    file_hmF2 = os.path.join(coeff_dir, dtime.strftime('%Y'),
                             dtime.strftime('%m%d'),
                             ('IRTAM_hmF2_COEFFS_' + time_str))

    F_hmF2 = IRTAM_read_files(file_hmF2)

    output = (F_B0, F_B1, F_f0F2, F_hmF2)

    return output


def IRTAM_read_files(filename):
    """Read IRTAM file.

    Parameters
    ----------
    filename : str
        Path to the IRTAM folder file.

    Returns
    -------
    F_IRTAM : array-like
        Array of IRTAM coefficients.

    Raises
    ------
    IOError
        If filename is unknown

    Notes
    -----
    This function reads IRTAM file and outputs [14, 96] array.

    """
    # Test that the desired file exists
    if not os.path.isfile(filename):
        raise IOError('unknown IRTAM coefficient file: {:}'.format(filename))

    # Read in the file
    full_array = []
    with open(filename, mode='r') as file_f:
        for line in file_f:
            if line[0] != '#':
                line_vals = np.fromstring(line, dtype=float, sep=' ')
                full_array = np.concatenate((full_array, line_vals), axis=None)

    # Assign the file input into separate arrays
    array_main = full_array[0:988]
    array_add = full_array[988:]

    # Pull the predefined sizes of the function extensions
    coef = IRTAM_highest_power_of_extension()

    # For IRTAM: reshape array to [nj, nk] shape
    F_CCIR = np.zeros((coef['nj']['F0F2'], coef['nk']['F0F2']))
    F_CCIR_like = np.reshape(array_main, F_CCIR.shape, order='F')

    # Insert column between 0 and 1, for additional b0 coefficients
    F_IRTAM = np.zeros((coef['nj']['IRTAM'], coef['nk']['IRTAM']))
    F_IRTAM[0, :] = F_CCIR_like[0, :]
    F_IRTAM[1, :] = array_add
    F_IRTAM[2:, :] = F_CCIR_like[1:, :]

    return F_IRTAM


def IRTAM_gamma(G, D, F_B0, F_B1, F_foF2, F_hmF2):
    """Calculate foF2, M3000 propagation parameter, and foEs.

    Parameters
    ----------
    G : array-like
        Global functions for F2 region.
    D : array-like
        Diurnal functions for F2 region.
    F_B0 : array-like
        IRTAM coefficients for B0.
    F_B1 : array-like
        IRTAM coefficients for B1.
    F_foF2 : array-like
        IRTAM coefficients for foF2.
    F_hmF2 : array-like
        IRTAM coefficients for hmF2.

    Returns
    -------
    gamma_B0 : array-like
        Thickness B0 in km.
    gamma_B1 : array-like
        Thickness B1 in km.
    gamma_foF2 : array-like
        Critical frequency of F2 layer in MHz.
    gamma_hmF2 : array-like
        Height of F2 layer.

    Notes
    -----
    This function calculates numerical maps for B0, B1, foF2, and hmF2
    using matrix multiplication

    References
    ----------
    Forsythe et al. (2023), PyIRI: Whole-Globe Approach to the
    International Reference Ionosphere Modeling Implemented in Python,
    Space Weather.

    """

    # Find numerical map
    gamma_B0 = np.matmul(np.matmul(D, F_B0), G)
    gamma_B1 = np.matmul(np.matmul(D, F_B1), G)
    gamma_foF2 = np.matmul(np.matmul(D, F_foF2), G)
    gamma_hmF2 = np.matmul(np.matmul(D, F_hmF2), G)

    return gamma_B0, gamma_B1, gamma_foF2, gamma_hmF2


def IRTAM_highest_power_of_extension():
    """Provide the highest power of extension.

    Returns
    -------
    const : dict
        Dictionary that has QM, nk, and nj parameters.

    Notes
    -----
    This function sets a common set of constants that define the power of
    expansions.
    QM = array of highest power of sin(x).
    nk = highest order of geographic extension.
    e.g. there are 76 functions in Table 3 on page 18 in Jones & Graham 1965.
    nj = highest order in diurnal variation.

    References
    ----------
    Forsythe et al. (2023), PyIRI: Whole-Globe Approach to the
    International Reference Ionosphere Modeling Implemented in Python,
    Space Weather.

    Jones, W. B., & Gallet, R. M. (1965). Representation of diurnal
    and geographic variations of ionospheric data by numerical methods,
    control of instability, ITU Telecommunication Journal , 32 (1), 18–28.

    """
    # Degree of extension
    QM_F0F2 = [12, 12, 9, 5, 2, 1, 1, 1, 1]
    QM_M3000 = [7, 8, 6, 3, 2, 1, 1]
    QM_Es_upper = [11, 12, 6, 3, 1]
    QM_Es_median = [11, 13, 7, 3, 1, 1]
    QM_Es_lower = [11, 13, 7, 1, 1]
    QM = {'F0F2': QM_F0F2, 'M3000': QM_M3000,
          'Es_upper': QM_Es_upper, 'Es_median': QM_Es_median,
          'Es_lower': QM_Es_lower}

    # Geographic
    nk_F0F2 = 76
    nk_IRTAM = 76
    nk_M3000 = 49
    nk_Es_upper = 55
    nk_Es_median = 61
    nk_Es_lower = 55
    nk = {'F0F2': nk_F0F2, 'M3000': nk_M3000,
          'Es_upper': nk_Es_upper, 'Es_median': nk_Es_median,
          'Es_lower': nk_Es_lower, 'IRTAM': nk_IRTAM}

    # Diurnal
    nj_F0F2 = 13
    nj_IRTAM = 14
    nj_M3000 = 9
    nj_Es_upper = 5
    nj_Es_median = 7
    nj_Es_lower = 5

    nj = {'F0F2': nj_F0F2, 'M3000': nj_M3000,
          'Es_upper': nj_Es_upper, 'Es_median': nj_Es_median,
          'Es_lower': nj_Es_lower, 'IRTAM': nj_IRTAM}

    const = {'QM': QM, 'nk': nk, 'nj': nj}

    return const


def IRTAM_find_hmF1(B0, B1, NmF2, hmF2, NmF1):
    """Return hmF1 for the given parameters.

    Parameters
    ----------
    B0 : array-like
        Thickness parameter in km.
    B1 : array-like
        Thickness parameter in km.
    NmF2 : array-like
        Peak of F2 layer in m-3.
    hmF2 : int
        Height of F2 layer in km.
    NmF1 : array-like
        Peak of F1 layer in m-3.

    Returns
    -------
    hmF1 : array-like
        Height of F1 layer in km.

    Notes
    -----
    This function returns height of F1 layer if the bottom of F2 is
    constructed using Ramakrishnan & Rawer equation.

    References
    ----------
    Bilitza et al. (2022), The International Reference Ionosphere
    model: A review and description of an ionospheric benchmark, Reviews
    of Geophysics, 60.

    """

    B0 = np.transpose(B0)
    B1 = np.transpose(B1)
    NmF2 = np.transpose(NmF2)
    hmF2 = np.transpose(hmF2)
    NmF1 = np.transpose(NmF1)

    # Create a random array of heights with high resolution
    h = np.arange(0, 700, 1)

    hmF1 = np.zeros((1, B0.size)) + np.nan

    a = np.where(np.isfinite(NmF1))[0]

    # Ramakrishnan_and_Rawer:
    for i in range(0, a.size):
        den = Ramakrishnan_Rawer_function(NmF2[a[i]], hmF2[a[i]],
                                          B0[a[i]], B1[a[i]], h)
        hmF1[0, a[i]] = np.interp(NmF1[a[i]], den, h)

    return hmF1


def IRTAM_freq_to_Nm(f):
    """Convert critical frequency to plasma density.

    Parameters
    ----------
    f : array-like
        Critical frequency in MHz.

    Returns
    -------
    Nm : array-like
       Peak density in m-3.

    Notes
    -----
    This function returns maximum density for the given critical frequency and
    limits it to 1 if it is below zero.

    """

    Nm = 0.124 * f**2 * 1e11

    # Exclude negative values, in case there are any
    Nm[np.where(Nm <= 0)] = 1.

    return Nm


def IRTAM_F2_top_thickness(foF2, hmF2, B_0, F107):
    """Return thicknesses of ionospheric layers.

    Parameters
    ----------
    foF2 : array-like
        Critical frequency of F2 region in MHz.
    hmF2 : array-like
        Height of the F2 layer.
    hmE : array-like
        Height of the E layer.
    mth : int
        Month of the year.
    F107 : array-like
        Solar flux index in SFU.

    Returns
    -------
    B_F2_top : array-like
        Thickness of F2 top in km.
    B_E_bot : array-like
        Thickness of E bottom in km.
    B_E_top : array-like
        Thickness of E top in km.

    Notes
    -----
    This function returns thicknesses of ionospheric layers.
    We assume that B0 from IRTAM is equivalent to the
    thickness of the bottom side formulated in PyIRI.
    In reality, it could be different, since PyIRI uses
    Epstein function for the bottom side and IRTAM uses
    Ramakrishnan & Rawer function.

    References
    ----------
    Forsythe et al. (2023), PyIRI: Whole-Globe Approach to the
    International Reference Ionosphere Modeling Implemented in Python,
    Space Weather.

    """

    # B_F2_top................................................................
    # Shape parameter depends on solar activity:
    # Effective sunspot number
    R12 = ml.F107_2_R12(F107)
    k = (3.22 - 0.0538 * foF2 - 0.00664 * hmF2 + (0.113 * hmF2 / B_0)
         + 0.00257 * R12)

    # Auxiliary parameters x and v:
    x = (k * B_0 - 150.) / 100.
    # Thickness
    B_F2_top = (100. * x + 150.) / (0.041163 * x**2 - 0.183981 * x + 1.424472)

    return B_F2_top


def IRTAM_reconstruct_density_from_parameters(F2, F1, E, alt):
    """Construct vertical EDP for 2 levels of solar activity.

    Parameters
    ----------
    F2 : dict
        Dictionary of parameters for F2 layer.
    F1 : dict
        Dictionary of parameters for F1 layer.
    E : dict
        Dictionary of parameters for E layer.
    alt : array-like
        1-D array of altitudes [N_V] in km.

    Returns
    -------
    EDP : array-like
        Electron density [N_V, N_G]
        in m-3.

    Notes
    -----
    This function calculates 3-D density from given dictionaries of
    the parameters.

    References
    ----------
    Forsythe et al. (2023), PyIRI: Whole-Globe Approach to the
    International Reference Ionosphere Modeling Implemented in Python,
    Space Weather.

    """
    s = F2['Nm'].shape
    N_G = s[1]

    x = np.full((12, N_G), np.nan)
    x[0, :] = F2['Nm'][0, :]
    x[1, :] = F1['Nm'][0, :]
    x[2, :] = E['Nm'][0, :]
    x[3, :] = F2['hm'][0, :]
    x[4, :] = F1['hm'][0, :]
    x[5, :] = E['hm'][0, :]
    x[6, :] = F2['B0'][0, :]
    x[7, :] = F2['B1'][0, :]
    x[8, :] = F2['B_top'][0, :]
    x[9, :] = F1['B_bot'][0, :]
    x[10, :] = E['B_bot'][0, :]
    x[11, :] = E['B_top'][0, :]

    EDP = IRTAM_EDP_builder(x, alt)

    return EDP


def IRTAM_EDP_builder(x, aalt):
    """Construct vertical EDP.

    Parameters
    ----------
    x : array-like
        Array where 1st dimension indicates the parameter (total 11
        parameters), second dimension is time, and third is horizontal grid
        [11, N_T, N_G].
    aalt : array-like
        1-D array of altitudes [N_V] in km.

    Returns
    -------
    density : array-like
        3-D electron density [N_T, N_V, N_G] in m-3.

    Notes
    -----
    This function builds the EDP from the provided parameters for all time
    frames, all vertical and all horizontal points.

    References
    ----------
    Forsythe et al. (2023), PyIRI: Whole-Globe Approach to the
    International Reference Ionosphere Modeling Implemented in Python,
    Space Weather.

    """

    # Number of elements in horizontal dimension of grid
    ngrid = x.shape[1]

    # vertical dimention
    nalt = aalt.size

    # Empty arrays
    density_F2 = np.zeros((nalt, ngrid))
    density_F1 = np.zeros((nalt, ngrid))
    density_E = np.zeros((nalt, ngrid))
    drop_1 = np.zeros((nalt, ngrid))
    drop_2 = np.zeros((nalt, ngrid))

    # Shapes:
    # for filling with altitudes because the last dimensions should match
    # the source
    shape1 = (ngrid, nalt)

    # For filling with horizontal maps because the last dimentsions should
    # match the source
    shape2 = (nalt, ngrid)

    order = 'F'
    NmF2 = np.reshape(x[0, :], ngrid, order=order)
    NmF1 = np.reshape(x[1, :], ngrid, order=order)
    NmE = np.reshape(x[2, :], ngrid, order=order)
    hmF2 = np.reshape(x[3, :], ngrid, order=order)
    hmF1 = np.reshape(x[4, :], ngrid, order=order)
    hmE = np.reshape(x[5, :], ngrid, order=order)
    B0 = np.reshape(x[6, :], ngrid, order=order)
    B1 = np.reshape(x[7, :], ngrid, order=order)
    B_F2_top = np.reshape(x[8, :], ngrid, order=order)
    B_F1_bot = np.reshape(x[9, :], ngrid, order=order)
    B_E_bot = np.reshape(x[10, :], ngrid, order=order)
    B_E_top = np.reshape(x[11, :], ngrid, order=order)

    # Set to some parameters if zero or lower:
    B_F1_bot[np.where(B_F1_bot <= 0)] = 10
    B_F2_top[np.where(B_F2_top <= 0)] = 30

    # Array of hmFs with same dimensions as result, to later search
    # using argwhere
    a_alt = np.full(shape1, aalt, order='F')
    a_alt = np.swapaxes(a_alt, 0, 1)

    # Fill arrays with parameters to add height dimension and populate it
    # with same values, this is important to keep all operations in matrix
    # form
    a_NmF2 = np.full(shape2, NmF2)
    a_NmF1 = np.full(shape2, NmF1)
    a_NmE = np.full(shape2, NmE)
    a_hmF2 = np.full(shape2, hmF2)
    a_hmF1 = np.full(shape2, hmF1)
    a_hmE = np.full(shape2, hmE)
    a_B_F2_top = np.full(shape2, B_F2_top)
    a_B0 = np.full(shape2, B0)
    a_B1 = np.full(shape2, B1)
    a_B_F1_bot = np.full(shape2, B_F1_bot)
    a_B_E_top = np.full(shape2, B_E_top)
    a_B_E_bot = np.full(shape2, B_E_bot)

    # Amplitude for Epstein functions
    a_A1 = 4. * a_NmF2
    a_A2 = 4. * a_NmF1
    a_A3 = 4. * a_NmE

    # !!! do not use a[0], because all 3 dimensions are needed. this is
    # the same as density[a]= density[a[0], a[1], a[2]]

    # F2 top (same for yes F1 and no F1)
    a = np.where(a_alt >= a_hmF2)
    density_F2[a] = ml.epstein_function_top_array(a_A1[a], a_hmF2[a],
                                                  a_B_F2_top[a], a_alt[a])

    # E bottom (same for yes F1 and no F1)
    a = np.where(a_alt <= a_hmE)
    density_E[a] = ml.epstein_function_array(a_A3[a], a_hmE[a], a_B_E_bot[a],
                                             a_alt[a])

    # when F1 is present-----------------------------------------
    # F2 bottom down to F1
    a = np.where((np.isfinite(a_NmF1)) & (a_alt < a_hmF2) & (a_alt >= a_hmF1))
    density_F2[a] = Ramakrishnan_Rawer_function(a_NmF2[a], a_hmF2[a],
                                                a_B0[a], a_B1[a], a_alt[a])

    # E top plus F1 bottom (hard boundaries)
    a = np.where((a_alt > a_hmE) & (a_alt < a_hmF1))
    drop_1[a] = 1. - ((a_alt[a] - a_hmE[a]) / (a_hmF1[a] - a_hmE[a]))**4.
    drop_2[a] = 1. - ((a_hmF1[a] - a_alt[a]) / (a_hmF1[a] - a_hmE[a]))**4.

    density_E[a] = ml.epstein_function_array(a_A3[a],
                                             a_hmE[a],
                                             a_B_E_top[a],
                                             a_alt[a]) * drop_1[a]
    density_F1[a] = ml.epstein_function_array(a_A2[a],
                                              a_hmF1[a],
                                              a_B_F1_bot[a],
                                              a_alt[a]) * drop_2[a]

    # When F1 is not present(hard boundaries)--------------------
    a = np.where((np.isnan(a_NmF1)) & (a_alt < a_hmF2) & (a_alt > a_hmE))
    drop_1[a] = 1.0 - ((a_alt[a] - a_hmE[a]) / (a_hmF2[a] - a_hmE[a]))**4.0
    drop_2[a] = 1.0 - ((a_hmF2[a] - a_alt[a]) / (a_hmF2[a] - a_hmE[a]))**4.0
    density_E[a] = ml.epstein_function_array(a_A3[a], a_hmE[a], a_B_E_top[a],
                                             a_alt[a]) * drop_1[a]

    density_F2[a] = Ramakrishnan_Rawer_function(a_NmF2[a], a_hmF2[a], a_B0[a],
                                                a_B1[a], a_alt[a]) * drop_2[a]
    density = density_F2 + density_F1 + density_E

    # Make 1 everything that is <= 0
    density[np.where(density <= 1.0)] = 1.0

    return density


def Ramakrishnan_Rawer_function(NmF2, hmF2, B0, B1, h):
    """Construct density Ramakrishnan & Rawer F2 bottomside.

    Parameters
    ----------
    NmF2 : array-like
        F2 region peak in m-3.
    hmF2 : array-like
        Height of F2 layer in km.
    B0 : array-like
        Thickness parameter for F2 region in km.
    B1 : array-like
        Thickness parameter for F2 region in km.
    h : array-like
        Altitude in km.

    Returns
    -------
    den : array-like
        Constructed density in m-3.

    Notes
    -----
    This function constructs bottomside of F2 layer using
    Ramakrishnan & Rawer equation (as in IRI). All inputs are supposed
    to have same size.

    References
    ----------
    Bilitza et al. (2022), The International Reference Ionosphere
    model: A review and description of an ionospheric benchmark, Reviews
    of Geophysics, 60.

    """
    x = (hmF2 - h) / B0
    den = NmF2 * ml.fexp(-(np.sign(x) * (np.abs(x)**B1))) / np.cosh(x)

    return den


def call_IRTAM_PyIRI(aUT, dtime, alon, alat, aalt, f2, f1, e_peak, es_peak,
                     modip, TOV, coeff_dir, irtam_dir):
    """Update parameters and build EDP for IRTAM for one time frame.

    Parameters
    ----------
    aUT : array-like
        Time array that was used for PyIRI in hours.
    dtime : dtime object
        F2 region peak in m-3.
    alon : array-like
        Longitudes 1-D array in degrees.
    alat : array-like
        Latitudes 1-D array in degrees.
    aalt : array-like
        Altitude 1-D array in km for EDP construction.
    f2 : dict
        'Nm' is peak density of F2 region in m-3.
        'fo' is critical frequency of F2 region in MHz.
        'M3000' is the obliquity factor for a distance of 3,000 km.
        Defined as refracted in the ionosphere, can be received at a
        distance of 3,000 km, unitless.
        'hm' is height of the F2 peak in km.
        'B_topi is top thickness of the F2 region in km.
        'B_bot' is bottom thickness of the F2 region in km.
        Shape [N_T, N_G].
    f1 : dict
        'Nm' is peak density of F1 region in m-3.
        'fo' is critical frequency of F1 region in MHz.
        'P' is the probability occurrence of F1 region, unitless.
        'hm' is height of the F1 peak in km.
        'B_bot' is bottom thickness of the F1 region in km.
        Shape [N_T, N_G].
    e_peak : dict
        'Nm' is peak density of E region in m-3.
        'fo' is critical frequency of E region in MHz.
        'hm' is height of the E peak in km.
        'B_top' is bottom thickness of the E region in km.
        'B_bot' is bottom thickness of the E region in km.
        Shape [N_T, N_G].
    es_peak : dict
        'Nm' is peak density of Es region in m-3.
        'fo' is critical frequency of Es region in MHz.
        'hm' is height of the Es peak in km.
        'B_top' is bottom thickness of the Es region in km.
        'B_bot' is bottom thickness of the Es region in km.
        Shape [N_T, N_G].
    modip : array-like
        Modified dip angle in degrees.
    TOV : float
        Time of Validity in decimal hours. Use 24 if not known.
    coeff_dir : str
        Direction of IRI coefficients.
    irtam_dir : str
        Direction of IRTAM coefficients.

    Returns
    -------
    f2 : dict
        'Nm' is peak density of F2 region in m-3.
        'hm' is height of the F2 peak in km.
        'B_top is top thickness of the F2 region in km.
        'B0' is bottom thickness parameter of the F2 region in km.
        'B1' is bottom thickness parameter of the F2 region in km.
        Shape [N_T, N_G].
    f1 : dict
        'Nm' is peak density of F1 region in m-3.
        'hm' is height of the F1 peak in km.
        'B_bot' is bottom thickness of the F1 region in km.
        Shape [N_T, N_G].
    e_peak : dict
        'Nm' is peak density of E region in m-3.
        'hm' is height of the E peak in km.
        'B_top' is bottom thickness of the E region in km.
        'B_bot' is bottom thickness of the E region in km.
        Shape [N_T, N_G].
    es_peak : dict
        'Nm' is peak density of Es region in m-3.
        'hm' is height of the Es peak in km.
        'B_top' is bottom thickness of the Es region in km.
        'B_bot' is bottom thickness of the Es region in km.
        Shape [N_T, N_G].
    EDP_result : array-like
        Electron density profile in m-3. Shape [N_T, N_V, N_G].

    Notes
    -----
    This function uses IRTAM coefficients to construct NmF2, hmF2, B0, B1
    maps, collects other parameters from PyIRI, updates hmF1 and B_F1_bot,
    and constructs the EDP.

    """
    # Find time index
    UT = dtime.hour + dtime.minute / 60.0 + dtime.second / 3600.0
    it = np.where(aUT == UT)[0]

    # Find IRTAM parameters
    IRTAM_f2 = IRTAM_density(dtime,
                             alon,
                             alat,
                             modip,
                             TOV,
                             coeff_dir,
                             irtam_dir)

    # Create empty arrays with needed shape for 1 time frame
    # to fill with updated values
    shape = IRTAM_f2['fo'].shape
    NmF1 = np.zeros((shape))
    NmE = np.zeros((shape))
    hmE = np.zeros((shape))
    B_F2_top = np.zeros((shape))
    B_E_bot = np.zeros((shape))
    B_E_top = np.zeros((shape))
    P_F1 = np.zeros((shape))
    NmEs = np.zeros((shape))
    hmEs = np.zeros((shape))
    B_Es_bot = np.zeros((shape))
    B_Es_top = np.zeros((shape))
    hmF1 = np.zeros((shape))
    B_F2_top = np.zeros((shape))

    # Fill with PyIRI parameters that will not
    # need to be updated
    NmF1[:, :] = f1['Nm'][it, :]
    NmE[:, :] = e_peak['Nm'][it, :]
    hmE[:, :] = e_peak['hm'][it, :]
    B_F2_top[:, :] = f2['B_top'][it, :]
    B_E_bot[:, :] = f1['P'][it, :]
    B_E_top[:, :] = e_peak['B_top'][it, :]
    P_F1[:, :] = f1['P'][it, :]
    NmEs[:, :] = es_peak['Nm'][it, :]
    hmEs[:, :] = es_peak['hm'][it, :]
    B_Es_bot[:, :] = es_peak['B_bot'][it, :]
    B_Es_top[:, :] = es_peak['B_top'][it, :]
    B_F2_top[:, :] = f2['B_top'][it, :]

    # UPDATING PARAMETERS that depend of NmF2, hmF2, and thickness:
    # Convert critical frequency to the electron density (m-3)
    NmF2 = IRTAM_freq_to_Nm(IRTAM_f2['fo'])
    hmF1 = IRTAM_find_hmF1(IRTAM_f2['B0'], IRTAM_f2['B1'], NmF2,
                           IRTAM_f2['hm'], NmF1)
    B_F1_bot = ml.find_B_F1_bot(hmF1, hmE, P_F1)

    # combine parameters from PyIRI and IRTAM to merged dictionary
    F2_result = {'Nm': NmF2,
                 'hm': IRTAM_f2['hm'],
                 'B_top': B_F2_top,
                 'B0': IRTAM_f2['B0'],
                 'B1': IRTAM_f2['B1']}
    F1_result = {'Nm': NmF1,
                 'hm': hmF1,
                 'B_bot': B_F1_bot}
    E_result = {'Nm': NmE,
                'hm': hmE,
                'B_bot': B_E_bot,
                'B_top': B_E_top}
    Es_result = {'Nm': NmEs,
                 'hm': hmEs,
                 'B_bot': B_Es_bot,
                 'B_top': B_Es_top}

    EDP_result = IRTAM_reconstruct_density_from_parameters(F2_result,
                                                           F1_result,
                                                           E_result,
                                                           aalt)

    return F2_result, F1_result, E_result, Es_result, EDP_result


def run_PyIRTAM(year, month, day, aUT, alon, alat, aalt, F107, irtam_dir):
    """Update parameters and build EDP for IRTAM for one time frame.

    Parameters
    ----------
    year : int
        Year.
    mth : int
        Month of year.
    aUT : array-like
        Array of universal time (UT) in hours. Must be Numpy array of any size
        [N_T].
    alon : array-like
        Flattened array of geographic longitudes in degrees. Must be Numpy
        array of any size [N_G].
    alat : array-like
        Flattened array of geographic latitudes in degrees. Must be Numpy array
        of any size [N_G].
    aalt : array-like
        Array of altitudes in km. Must be Numpy array of any size [N_V].
    F107 : float
        User provided F10.7 solar flux index in SFU.
    irtam_dir : str
        Place where IRTAM coefficients are on user's local computer.

    Returns
    -------
    f2_b : dict
        F2 parameters form PyIRI
        'Nm' is peak density of F2 region in m-3.
        'fo' is critical frequency of F2 region in MHz.
        'M3000' is the obliquity factor for a distance of 3,000 km.
        Defined as refracted in the ionosphere, can be received at a distance
        of 3,000 km, unitless.
        'hm' is height of the F2 peak in km.
        'B_topi is top thickness of the F2 region in km.
        'B_bot' is bottom thickness of the F2 region in km.
        Shape [N_T, N_G, 2].
    f1_b : dict
        F1 parameters form PyIRI
        'Nm' is peak density of F1 region in m-3.
        'fo' is critical frequency of F1 region in MHz.
        'P' is the probability occurrence of F1 region, unitless.
        'hm' is height of the F1 peak in km.
        'B_bot' is bottom thickness of the F1 region in km.
        Shape [N_T, N_G, 2].
    e_b : dict
        E parameters form PyIRI
        'Nm' is peak density of E region in m-3.
        'fo' is critical frequency of E region in MHz.
        'hm' is height of the E peak in km.
        'B_top' is bottom thickness of the E region in km.
        'B_bot' is bottom thickness of the E region in km.
        Shape [N_T, N_G, 2].
    es_b : dict
        Es parameters form PyIRI
        'Nm' is peak density of Es region in m-3.
        'fo' is critical frequency of Es region in MHz.
        'hm' is height of the Es peak in km.
        'B_top' is bottom thickness of the Es region in km.
        'B_bot' is bottom thickness of the Es region in km.
        Shape [N_T, N_G, 2].
    sun : dict
        'lon' is longitude of subsolar point in degrees.
        'lat' is latitude of subsolar point in degrees.
        Shape [N_G].
    mag : dict
        'inc' is inclination of the magnetic field in degrees.
        'modip' is modified dip angle in degrees.
        'mag_dip_lat' is magnetic dip latitude in degrees.
        Shape [N_G].
    edp_b : array-like
        Electron density profiles from PyIRI in m-3 with shape
        [N_T, N_V, N_G]
    f2_day : dict
        F2 parameters form PyIRTAM
        'Nm' is peak density of F2 region in m-3.
        'hm' is height of the F2 peak in km.
        'B_top is top thickness of the F2 region in km.
        'B0' is bottom thickness parameter of the F2 region in km.
        'B1' is bottom thickness parameter of the F2 region in km.
        Shape [N_T, N_G].
    f1_day : dict
        F1 parameters form PyIRTAM
        'Nm' is peak density of F1 region in m-3.
        'hm' is height of the F1 peak in km.
        'B_bot' is bottom thickness of the F1 region in km.
        Shape [N_T, N_G].
    e_day : dict
        E parameters form PyIRTAM
        'Nm' is peak density of E region in m-3.
        'hm' is height of the E peak in km.
        'B_top' is bottom thickness of the E region in km.
        'B_bot' is bottom thickness of the E region in km.
        Shape [N_T, N_G].
    es_day : dict
        Es parameters form PyIRTAM
        'Nm' is peak density of Es region in m-3.
        'hm' is height of the Es peak in km.
        'B_top' is bottom thickness of the Es region in km.
        'B_bot' is bottom thickness of the Es region in km.
        Shape [N_T, N_G].
    edp_day : array-like
        Electron density profile from PyIRTAM in m-3. Shape
        [N_T, N_V, N_G].

    Notes
    -----
    This function runs PyIRTAM for a day of interest.

    """
    # First, determine the standard PyIRI parameters for the day of interest
    # It is better to do it in the beginning (outside the time loop),
    # so that PyIRI is called only once for the whole day.

    # Use CCIR (not URSI) since IRTAM uses CCIR models.
    ccir_or_ursi = 0  # 0 = CCIR, 1 = URSI

    # Run PyIRI
    f2_b, f1_b, e_b, es_b, sun, mag, edp_b = ml.IRI_density_1day(
        year, month, day, aUT, alon, alat, aalt, F107, PyIRI.coeff_dir,
        ccir_or_ursi)

    # Create empty dictionaries to store daily parameters.
    empt = np.array([])
    f2_day = {'Nm': empt, 'hm': empt, 'B0': empt, 'B1': empt, 'B_top': empt}
    f1_day = {'Nm': empt, 'hm': empt, 'B_bot': empt}
    e_day = {'Nm': empt, 'hm': empt, 'B_bot': empt, 'B_top': empt}
    es_day = {'Nm': empt, 'hm': empt, 'B_bot': empt, 'B_top': empt}
    edp_day = edp_b * 0.
    f1_day['P'] = f1_b['P']

    for it in range(0, aUT.size):
        # Dtime for one time frame
        hour = int(np.fix(aUT[it]))
        minute = int((aUT[it] - hour) * 60.)
        dtime = dt.datetime(year, month, day, hour, minute, 0)

        # Call PyIRTAM:
        F2, F1, E, Es, EDP = call_IRTAM_PyIRI(aUT,
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
        # Save results.
        if it == 0:
            for key in F2:
                f2_day[key] = F2[key][:]
            for key in F1:
                f1_day[key] = F1[key][:]
            for key in E:
                e_day[key] = E[key][:]
            for key in Es:
                es_day[key] = Es[key][:]
        else:
            for key in F2:
                f2_day[key] = np.concatenate((f2_day[key], F2[key][:]), axis=0)
            for key in F1:
                f1_day[key] = np.concatenate((f1_day[key], F1[key][:]), axis=0)
            for key in E:
                e_day[key] = np.concatenate((e_day[key], E[key][:]), axis=0)
            for key in Es:
                es_day[key] = np.concatenate((es_day[key], Es[key][:]), axis=0)
        edp_day[it, :, :] = EDP

    return (f2_b, f1_b, e_b, es_b, sun, mag, edp_b, f2_day, f1_day, e_day,
            es_day, edp_day)
