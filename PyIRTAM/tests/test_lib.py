#!/usr/bin/env python
# --------------------------------------------------------
"""Unit tests for PyIRTAM.lib functions."""

import datetime as dt
import numpy as np
import os
import pytest

from PyIRTAM import lib


class TestIRTAMErrors(object):
    """Test class for IRTAM error catches."""

    def setup_method(self):
        """Initialize all tests."""
        self.bad_dir = "bad_path"
        self.bad_file = "bad_file.txt"

        return

    def teardown_method(self):
        """Tear down to clean the test environment."""

        del self.bad_dir, self.bad_file

        return

    def test_bad_filename(self):
        """Test IOError raised with a bad filename."""

        with pytest.raises(IOError) as ierr:
            lib.IRTAM_read_files(os.path.join(self.bad_dir, self.bad_file))

        assert str(ierr).find('unknown IRTAM coefficient file') >= 0
        return

    def test_bad_coeff_dir(self):
        """Test IOError raised with a bad coefficient directory."""

        with pytest.raises(IOError) as ierr:
            lib.IRTAM_read_coeff(dt.datetime(1999, 1, 1), self.bad_dir)

        assert str(ierr).find('unknown IRTAM coefficient file') >= 0
        return


def test_IRTAM_EDP_builder_updated_shape_and_validity():
    """Test IRTAM_EDP_builder_updated output shape and regression correctness."""
    aalt = np.arange(100, 500, 20)
    x = np.array([[1.95159501e+12],
                  [1.08274005e+12],
                  [1.45001680e+11],
                  [3.26385692e+02],
                  [2.39831415e+02],
                  [1.10000000e+02],
                  [1.55355103e+02],
                  [1.43353497e+00],
                  [3.15333852e+01],
                  [6.49157075e+01],
                  [8.99941343e-01],
                  [7.00000000e+00]])

    res = lib.IRTAM_EDP_builder_updated(x, aalt)

    expected = np.array([
        [8.66186261e+06],
        [1.21314491e+11],
        [4.47391265e+11],
        [7.01589531e+11],
        [8.67220541e+11],
        [9.83493825e+11],
        [1.05722190e+12],
        [1.08471935e+12],
        [1.32441004e+12],
        [1.56306769e+12],
        [1.77738327e+12],
        [1.92984908e+12],
        [1.87195709e+12],
        [1.57630111e+12],
        [1.23669885e+12],
        [9.44602954e+11],
        [7.19478755e+11],
        [5.53017754e+11],
        [4.31221894e+11],
        [3.41737238e+11],
    ])

    assert res.shape == expected.shape, "Output shape mismatch"
    assert np.all(res > 0), "Electron density must be positive"
    assert np.all(np.isfinite(res)), "Electron density must be finite"
    assert np.allclose(res, expected, rtol=1e-6), "Regression output mismatch"