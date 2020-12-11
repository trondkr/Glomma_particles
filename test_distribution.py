import unittest
from config_sedimentdrift import MartiniConf
from sedimentdrift import SedimentDrift
from bathymetry import Bathymetry
from probability_distribution_map_v2 import SedimentDistribution
from config_plot import ConfigPlot
import pandas as pd
import numpy as np
import xarray as xr


class TestSedimentDistribution(unittest.TestCase):

    def setUp(self):
        super(TestSedimentDistribution, self).setUp()

        self.distribution = SedimentDistribution()

    def tearDown(self) -> None:
        super(TestSedimentDistribution, self).tearDown()
        self.config = None

    def test_setup_returns_config_object(self):
        self.assertIsNotNone(self.distribution.config_sedimentdrift)
        self.assertIsInstance(self.distribution.config_sedimentdrift, MartiniConf)

    def test_init_sediment_distribution_class(self):
        bathymetry = Bathymetry(self.distribution.config_sedimentdrift)
        self.assertIsInstance(self.distribution.bath, Bathymetry)
        self.assertIsNotNone(bathymetry.config)

    def test_index_of_last_valid_position(self):
        time = np.arange(0, 10, 1)
        trajectory = np.ones(2)
        test_var = np.ones((len(time), len(trajectory)))
        test_var[0:3, 0] = np.nan
        test_var[0:5, 1] = np.nan
        test_var[-2:, 1] = np.nan

        # The test array looks like this:
        # [[nan nan nan  1.  1.  1.  1.  1.  1.  1.]
        #  [nan nan nan nan nan  1.  1.  1. nan nan]]

        da = xr.DataArray(data=test_var, dims=["time", "trajectory"],
                          coords=[time, trajectory])
        self.assertIsInstance(da, xr.DataArray)

        ds = da.to_dataset(name="test_var")
        self.assertIsInstance(ds, xr.Dataset)

        res = self.distribution.get_indexes_of_last_valid_position(ds, var_name="test_var")
        index_array_expected = [9, 7]
        np.testing.assert_array_equal(res, index_array_expected)

    def test_index_of_last_valid_position_all_valid(self):
        time = np.arange(0, 10, 1)
        trajectory = np.ones(2)
        test_var = np.ones((len(time), len(trajectory)))

        da = xr.DataArray(data=test_var, dims=["time", "trajectory"],
                          coords=[time, trajectory])
        self.assertIsInstance(da, xr.DataArray)

        ds = da.to_dataset(name="test_var")
        self.assertIsInstance(ds, xr.Dataset)

        res = self.distribution.get_indexes_of_last_valid_position(ds, var_name="test_var")
        index_array_expected = [9, 9]
        np.testing.assert_array_equal(res, index_array_expected)

    def test_index_of_last_valid_position_when_non_valid(self):
        time = np.arange(0, 10, 1)
        trajectory = np.ones(2)
        test_var = np.ones((len(time), len(trajectory)))

        test_var[:,:]=np.nan

        da = xr.DataArray(data=test_var, dims=["time", "trajectory"],
                          coords=[time, trajectory])
        self.assertIsInstance(da, xr.DataArray)

        ds = da.to_dataset(name="test_var")
        self.assertIsInstance(ds, xr.Dataset)

        res = self.distribution.get_indexes_of_last_valid_position(ds, var_name="test_var")

        index_array_expected = []
        np.testing.assert_array_equal(res, index_array_expected)

    def test_index_of_last_valid_position_when_one_valid_and_one_not_valid(self):
        time = np.arange(0, 10, 1)
        trajectory = np.ones(2)
        test_var = np.ones((len(time), len(trajectory)))

        test_var[:,0]=np.nan

        da = xr.DataArray(data=test_var, dims=["time", "trajectory"],
                          coords=[time, trajectory])
        self.assertIsInstance(da, xr.DataArray)

        ds = da.to_dataset(name="test_var")
        self.assertIsInstance(ds, xr.Dataset)

        res = self.distribution.get_indexes_of_last_valid_position(ds, var_name="test_var")

        index_array_expected = [9]
        np.testing.assert_array_equal(res, index_array_expected)


if __name__ == "__main__":
    unittest.main()
