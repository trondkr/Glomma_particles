import unittest
import run_sedimentdrift
from datetime import datetime
from config_sedimentdrift import MartiniConf
from sedimentdrift import SedimentDrift
import numpy as np
from config_plot import ConfigPlot
from typing import List
import matplotlib
from bathymetry import Bathymetry
from config_plot import ConfigPlot

class TestBathymetry(unittest.TestCase):

    def setUp(self):
        super(TestBathymetry, self).setUp()

        self.config = ConfigPlot()

    def tearDown(self) -> None:
        super(TestBathymetry, self).tearDown()
        self.config=None

    def test_setup_returns_config_object(self):
        self.assertIsNotNone(self.config)
        self.assertIsInstance(self.config, ConfigPlot)

    def test_init_bathymetry_class(self):
        config_sediment = MartiniConf()
        bathymetry = Bathymetry(config_sediment)
        self.assertIsInstance(bathymetry, Bathymetry)
        self.assertIsNotNone(bathymetry.config)

    def test_bathymetry_config_correct_class(self):
        config_sediment = ConfigPlot()
        bathymetry = Bathymetry(config_sediment)
        self.assertIsInstance(bathymetry.config, ConfigPlot)

    def test_bathymetry_config_initialize_nonempty_ax(self):
        config_sediment = ConfigPlot()
        bathymetry = Bathymetry(config_sediment)
        self.assertIsNotNone(bathymetry.config.ax)


if __name__ == "__main__":
    unittest.main()
