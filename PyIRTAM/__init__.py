"""Core library imports for PyIRTAM."""

try:
    from importlib import metadata
except ImportError:
    import importlib_metadata as metadata

# Import the package modules and top-level classes
from PyIRTAM import main_library  # noqa F401

# Set version
__version__ = metadata.version('PyIRTAM')
