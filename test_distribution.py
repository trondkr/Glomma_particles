import unittest
from config_sedimentdrift import MartiniConf
from sedimentdrift import SedimentDrift
from bathymetry import Bathymetry
from probability_distribution_map_v2 import SedimentDistribution
from config_plot import ConfigPlot

class TestSedimentDistribution(unittest.TestCase):

    def setUp(self):
        super(TestSedimentDistribution, self).setUp()

        self.distribution = SedimentDistribution()

    def tearDown(self) -> None:
        super(TestSedimentDistribution, self).tearDown()
        self.config=None

    def test_setup_returns_config_object(self):
        self.assertIsNotNone(self.distribution.config_sedimentdrift)
        self.assertIsInstance(self.distribution.config_sedimentdrift, MartiniConf)

    def test_init_sediment_distribution_class(self):
        bathymetry = Bathymetry(self.distribution.config_sedimentdrift)
        self.assertIsInstance(self.distribution.bath, Bathymetry)
        self.assertIsNotNone(bathymetry.config)


if __name__ == "__main__":
    unittest.main()
