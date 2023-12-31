"""Core library imports for PyIRTAM."""

osflag = False
try:
    from importlib import metadata
    from importlib import resources
except ImportError:
    import importlib_metadata as metadata
    import os
    osflag = True

# Import the package modules and top-level classes
from PyIRTAM import main_library  # noqa F401

# Set version
__version__ = metadata.version('PyIRTAM')
