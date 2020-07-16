import unittest
import sedimentdrift

from datetime import datetime
import numpy as np


class TestGLOMMA_init(unittest.TestCase):

    def setUp(self):
        self.element = sedimentdrift.SedimentElement()


class TestInit(TestGLOMMA_init):

    def test_init_of_sediments(self):
        self.assertTrue(self.element.variables)


if __name__ == "__main__":
    unittest.main()
