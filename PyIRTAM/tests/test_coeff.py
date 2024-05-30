#!/usr/bin/env python
# --------------------------------------------------------
"""Unit tests for PyIRTAM.coeff functions."""

import datetime as dt
import os
import pytest

import PyIRTAM


class TestCoeffFilename(object):
    """Test class for coefficient filename construction."""

    def setup_method(self):
        """Initialize all tests."""
        self.dtime = dt.datetime(2021, 1, 1, 1, 1, 1)
        self.out = None
        return

    def teardown_method(self):
        """Tear down to clean the test environment."""

        del self.dtime, self.out
        return

    @pytest.mark.parametrize("param", ["B0", "B1", "hmF2", "foF2", "bad"])
    def test_get_itram_param_filename_with_subdirs(self, param):
        """Test the creation of different parameter filenames with subdirs.

        Parameters
        ----------
        param : str
            Coefficient parameter

        """

        self.out = PyIRTAM.coeff.get_irtam_param_filename(self.dtime, param,
                                                          use_subdirs=True)

        assert self.out.find(param) >= 0, "parameter missing from filename"
        assert self.out.find(PyIRTAM.irtam_coeff_dir) == 0, "missing root dir"

        self.out, _ = os.path.split(self.out)
        assert self.out.find(self.dtime.strftime("%Y")) > 0, "missing year dir"
        assert self.out.find(
            self.dtime.strftime("%m%d")) > 0, "missing month-day dir"
        return

    @pytest.mark.parametrize("param", ["B0", "B1", "hmF2", "foF2", "bad"])
    def test_get_itram_param_filename_without_subdirs(self, param):
        """Test the creation of different parameter filenames with subdirs.

        Parameters
        ----------
        param : str
            Coefficient parameter

        """

        self.out = PyIRTAM.coeff.get_irtam_param_filename(self.dtime, param,
                                                          use_subdirs=False)

        assert self.out.find(param) >= 0, "parameter missing from filename"
        assert self.out.find(PyIRTAM.irtam_coeff_dir) == 0, "missing root dir"

        self.out, _ = os.path.split(self.out)
        assert self.out.find(self.dtime.strftime("%Y")) < 0, "has year dir"
        assert self.out.find(
            self.dtime.strftime("%m%d")) < 0, "has month-day dir"
        return

    @pytest.mark.parametrize("param", ["B0", "B1", "hmF2", "foF2", "bad"])
    def test_get_itram_param_filename_irtamdir(self, param):
        """Test the creation of different parameter filenames with subdirs.

        Parameters
        ----------
        param : str
            Coefficient parameter

        """

        self.out = PyIRTAM.coeff.get_irtam_param_filename(self.dtime, param,
                                                          irtam_dir='test')

        assert self.out.find(param) >= 0, "parameter missing from filename"
        assert self.out.find(PyIRTAM.irtam_coeff_dir) < 0, "wrong root dir"
        assert self.out.find("test") == 0, "missing root dir"
        return


class TestCoeffDownload(object):
    """Test class for coefficient retrieval."""

    def setup_method(self):
        """Initialize all tests."""
        self.dtime = dt.datetime(2021, 1, 1, 1, 1, 1)
        self.package_irtam_dir = PyIRTAM.irtam_coeff_dir
        self.test_dir = os.path.join(os.path.split(PyIRTAM.irtam_coeff_dir)[0],
                                     "tests", "test_coeff")
        self.out = None
        return

    def teardown_method(self):
        """Tear down to clean the test environment."""

        # Ensure the package directory is correct
        if self.package_irtam_dir != PyIRTAM.irtam_coeff_dir:
            PyIRTAM.irtam_coeff_dir = self.package_irtam_dir

        # Remove the test directory, if it exists HERE

        del self.dtime, self.out
        return
