#!/usr/bin/env python
# --------------------------------------------------------
"""Unit tests for PyIRTAM.coeff functions."""

import datetime as dt
import os
import pytest
import shutil

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
        self.param = "B0"
        self.dstat = None
        self.fstat = None
        self.msg = None
        self.test_file = ''
        return

    def teardown_method(self):
        """Tear down to clean the test environment."""

        # Ensure the package directory is correct
        if self.package_irtam_dir != PyIRTAM.irtam_coeff_dir:
            PyIRTAM.irtam_coeff_dir = self.package_irtam_dir

        # Remove the test directory/ies and file, if present
        if os.path.isdir(self.test_dir):
            shutil.rmtree(self.test_dir)

        del self.dtime, self.package_irtam_dir, self.test_dir, self.dstat
        del self.fstat, self.msg, self.param, self.test_file
        return

    def eval_downloaded_contents(self, use_subdirs=True):
        """Evaluate the contents of the download directory.

        Parameters
        ----------
        use_subdirs : bool
            If True there should be subdirectories

        """
        # Test the subdirectory structure
        if use_subdirs:
            dirlist = os.listdir(self.test_dir)
            assert len(
                dirlist) == 1, "unexpected number of subdirs: {:}".format(
                    dirlist)
            assert dirlist[0].find(self.dtime.strftime(
                "%Y")) == 0, "unexpected dir name: {:}".format(dirlist[0])

            self.test_file = os.path.join(self.test_dir, dirlist[0])
            dirlist = os.listdir(self.test_file)
            assert len(
                dirlist) == 1, "unexpected number of subdirs: {:}".format(
                    dirlist)
            assert dirlist[0].find(self.dtime.strftime(
                "%m%d")) == 0, "unexpected dir name: {:}".format(dirlist[0])

            # Set the test file directory
            self.test_file = os.path.join(self.test_file, dirlist[0])
        else:
            # Set the test file directory
            self.test_file = self.test_dir

        # Test the downloaded file
        dirlist = os.listdir(self.test_file)
        assert len(dirlist) == 1, "unexpected number of files: {:}".format(
            dirlist)

        self.test_file = os.path.join(self.test_file, dirlist[0])
        assert self.test_file.find(self.dtime.strftime(
            self.param)) > 0, "unexpected filename: {:}".format(self.test_file)
        assert os.path.isfile(self.test_file), "not a file: {:}".format(
            self.test_file)
        return

    def test_download_w_subdir(self):
        """Test successful download with subdirectories."""
        # Download the desired file
        self.dstat, self.fstat, self.msg = PyIRTAM.coeff.download_irtam_coeffs(
            self.dtime, self.param, irtam_dir=self.test_dir, use_subdirs=True)

        # Test the directory and file status
        self.eval_downloaded_contents(use_subdirs=True)

        # Test the return status
        assert self.dstat, "data not downloaded: {:}".format(self.msg)
        assert self.fstat, "file not saved: {:}".format(self.msg)
        assert len(self.msg) == 0, "unexpected message: {:}".format(self.msg)

        return

    def test_download_no_subdir(self):
        """Test successful download without subdirectories."""
        # Download the desired file
        self.dstat, self.fstat, self.msg = PyIRTAM.coeff.download_irtam_coeffs(
            self.dtime, self.param, irtam_dir=self.test_dir, use_subdirs=False)

        # Test the directory and file status
        self.eval_downloaded_contents(use_subdirs=False)

        # Test the return status
        assert self.dstat, "data not downloaded: {:}".format(self.msg)
        assert self.fstat, "file not saved: {:}".format(self.msg)
        assert len(self.msg) == 0, "unexpected message: {:}".format(self.msg)
        return

    def test_download_overwrite(self):
        """Test successful download with overwrite."""
        # Download the desired file for the first time
        self.test_download_no_subdir()

        # Download the desired file for the second time
        self.dstat, self.fstat, self.msg = PyIRTAM.coeff.download_irtam_coeffs(
            self.dtime, self.param, irtam_dir=self.test_dir, use_subdirs=False,
            overwrite=True)

        # Test the directory and file status
        self.eval_downloaded_contents(use_subdirs=False)

        # Test the return status
        assert self.dstat, "data not downloaded: {:}".format(self.msg)
        assert self.fstat, "file not saved: {:}".format(self.msg)
        assert self.msg.find(
            "Overwriting IRTAM param") >= 0, "unexpected message: {:}".format(
                self.msg)
        return

    def test_download_no_overwrite(self):
        """Test successful download with overwrite."""
        # Download the desired file for the first time
        self.test_download_no_subdir()

        # Download the desired file for the second time
        self.dstat, self.fstat, self.msg = PyIRTAM.coeff.download_irtam_coeffs(
            self.dtime, self.param, irtam_dir=self.test_dir, use_subdirs=False,
            overwrite=False)

        # Test the directory and file status
        self.eval_downloaded_contents(use_subdirs=False)

        # Test the return status
        assert not self.dstat, "data downloaded: {:}".format(self.msg)
        assert self.fstat, "file not saved: {:}".format(self.msg)
        assert self.msg.find(
            "coefficient file exists") > 0, "unexpected message: {:}".format(
                self.msg)
        return

    def test_download_package_dir(self):
        """Test successful download to the package directory."""
        # Change the package directory name
        PyIRTAM.irtam_coeff_dir = self.test_dir

        # Download the desired file
        self.dstat, self.fstat, self.msg = PyIRTAM.coeff.download_irtam_coeffs(
            self.dtime, self.param, use_subdirs=False)

        # Test the directory and file status
        self.eval_downloaded_contents(use_subdirs=False)

        # Test the return status
        assert self.dstat, "data not downloaded: {:}".format(self.msg)
        assert self.fstat, "file not saved: {:}".format(self.msg)
        assert len(self.msg) == 0, "unexpected message: {:}".format(self.msg)
        return

    @pytest.mark.parametrize("good_param", ["foF2", "hmF2", "B0", "B1"])
    def test_download_params(self, good_param):
        """Test successful download with all supported parameters.

        Parameters
        ----------
        good_param : str
            The good parameter names

        """
        # Download the desired file
        self.param = good_param
        self.dstat, self.fstat, self.msg = PyIRTAM.coeff.download_irtam_coeffs(
            self.dtime, self.param, irtam_dir=self.test_dir, use_subdirs=False)

        # Test the directory and file status
        self.eval_downloaded_contents(use_subdirs=False)

        # Test the return status
        assert self.dstat, "data not downloaded: {:}".format(self.msg)
        assert self.fstat, "file not saved: {:}".format(self.msg)
        assert len(self.msg) == 0, "unexpected message: {:}".format(self.msg)
        return

    def test_download_bad_param(self):
        """Test download failure with an unsupported parameter."""
        # Download the desired file
        self.param = "badParam"
        self.dstat, self.fstat, self.msg = PyIRTAM.coeff.download_irtam_coeffs(
            self.dtime, self.param, irtam_dir=self.test_dir, use_subdirs=False)

        # Test the return status
        assert not self.dstat, "data downloaded: {:}".format(self.msg)
        assert not self.fstat, "file saved: {:}".format(self.msg)
        assert self.msg.find(
            "Bad IRTAM coefficient") >= 0, "unexpected message: {:}".format(
                self.msg)
        return
