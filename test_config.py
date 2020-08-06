import unittest
import run_sedimentdrift
from datetime import datetime
from config_sedimentdrift import MartiniConf
from sedimentdrift import SedimentDrift
import numpy as np
from config_plot import ConfigPlot
from typing import List
import matplotlib.pyplot as plt
import matplotlib
from circle_of_distance import Circle_of_distance

class TestConfigPlot(unittest.TestCase):

    def setUp(self):
        super(TestConfigPlot, self).setUp()
        self.config_plot = ConfigPlot()

    def tearDown(self) -> None:
        super(TestConfigPlot, self).tearDown()
        self.config_plot=None

    def test_setup_returns_config_object(self):
        self.assertIsNotNone(self.config_plot)
        self.assertIsInstance(self.config_plot, ConfigPlot)

    def test_setup_returns_map_object(self):
        self.assertIsNotNone(self.config_plot.ax)

    def test_setup_correct_configured(self):

        extent = self.config_plot.get_map_extent()
        self.assertIsNotNone(extent)
        self.assertIsInstance(extent, List)
        self.assertTrue(len(extent)==4)

    def test_projection_defined(self):
        self.assertIsNotNone(self.config_plot.projection)

    def test_color_levels(self):
        levels=np.arange(-50, -10, 10)
        colors = self.config_plot.level_colormap(levels)
        self.assertIsNotNone(colors)
        self.assertIsInstance(colors, matplotlib.colors.LinearSegmentedColormap)

    def test_init_circle_class(self):
        circle_of_distance = Circle_of_distance()
        self.assertIsInstance(circle_of_distance, Circle_of_distance)

    def test_create_circle(self):
        circle_of_distance=Circle_of_distance()
        lons,lats=circle_of_distance.create_circle_with_radius(10, 10, 1)
        self.assertTrue(len(lons) == 360)
        self.assertTrue(len(lats) == 360)


if __name__ == "__main__":
    unittest.main()
