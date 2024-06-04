"""Core library imports for PyIRTAM."""

from importlib import metadata
from importlib import resources

if not hasattr(resources, 'files'):
    # The `files` object was introduced in Python 3.9
    resources = None
    import os

# Import the package modules and top-level classes
from PyIRTAM import coeff  # noqa F401
from PyIRTAM import lib  # noqa F401
from PyIRTAM.lib import run_PyIRTAM  # noqa F401

# Set version
__version__ = metadata.version('PyIRTAM')

# Set the package IRTAM coefficient directory
if resources is None:
    irtam_coeff_dir = os.path.join(os.path.realpath(os.path.dirname(__file__)),
                                   'irtam_coeffs')
else:
    irtam_coeff_dir = str(resources.files(__package__).joinpath('irtam_coeffs'))
