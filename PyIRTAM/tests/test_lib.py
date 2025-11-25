#!/usr/bin/env python
# --------------------------------------------------------
"""Unit tests for PyIRTAM.lib functions."""

import datetime as dt
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
