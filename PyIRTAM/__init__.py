"""Core library imports for PyIRTAM."""

from importlib import metadata
from importlib import resources
import logging

# Initialize the logger
logging.raiseExceptions = False
logger = logging.getLogger('PyIRTAM_logger')

# Import the package modules and top-level classes
from PyIRTAM import coeff  # noqa F401
from PyIRTAM import lib  # noqa F401
from PyIRTAM.lib import run_PyIRTAM  # noqa F401

# Set version
__version__ = metadata.version('PyIRTAM')

# Set the package IRTAM coefficient directory
irtam_coeff_dir = str(resources.files(__package__).joinpath('irtam_coeffs'))
