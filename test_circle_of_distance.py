import unittest

import numpy as np

import circle_of_distance as cs
from config_sedimentdrift import MartiniConf


class TestCircleOfDistance(unittest.TestCase):

    def setUp(self):
        super(TestCircleOfDistance, self).setUp()
        self.ccs = cs.Circle_of_distance()
        self.config_sedimentdrift = MartiniConf()

    def tearDown(self) -> None:
        super(TestCircleOfDistance, self).tearDown()
        self.config_sedimentdrift = None
        self.ccs = None

    def test_setup_correct(self):
        self.assertIsInstance(self.config_sedimentdrift, MartiniConf)
        self.assertIsInstance(self.ccs, cs.Circle_of_distance)

    def test_circle_of_distribution(self):
        X, Y = self.ccs.create_circle_with_radius(self.config_sedimentdrift.st_lats[0],
                                                  self.config_sedimentdrift.st_lons[0],
                                                  self.config_sedimentdrift.release_radius)
        self.assertIsNotNone(X)
        self.assertIsNotNone(Y)
        self.assertEqual(np.shape(X), (360,))
        self.assertEqual(np.shape(Y), (360,))
