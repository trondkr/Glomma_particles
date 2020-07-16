import unittest
import run_sedimentdrift
from datetime import datetime
from config_sedimentdrift import MartiniConf
from sedimentdrift import SedimentDrift

class TestGLOMMA_init(unittest.TestCase):

    def setUp(self):
        super(TestGLOMMA_init, self).setUp()
        self.sediment_organizer = run_sedimentdrift.Sediment_Organizer()
        self.sediment_organizer.confobj.start_date = datetime(2012, 2, 1)
        self.sediment_organizer.confobj.end_date = datetime(2012, 5, 1)
        self.sediment_organizer.confobj.species = "clay"

    def tearDown(self):
        super(TestGLOMMA_init, self).tearDown()

class TestSedimentDrift(TestGLOMMA_init):

    def test_setup_returns_sediment_object(self):
        o = self.sediment_organizer.setup_and_config_sediment_module()
        self.assertIsInstance(o, SedimentDrift)

    def test_setup_correct_configured(self):
        o = self.sediment_organizer.setup_and_config_sediment_module()
        conf = o.get_config('vertical_mixing:update_terminal_velocity')
        self.assertIsNotNone(conf)


class TestInit(TestGLOMMA_init):

    def test_init_of_sediments(self):
        self.assertTrue(self.sediment_organizer)

    def test_correct_config_class(self):
        self.assertIsInstance(self.sediment_organizer.confobj, MartiniConf)

    def test_start_and_end_dates_correct_class(self):
        self.assertIsInstance(self.sediment_organizer.confobj.start_date, datetime)
        self.assertIsInstance(self.sediment_organizer.confobj.end_date, datetime)

    def test_output_filenames_created_correctly(self):
        expected=self.sediment_organizer.confobj.outputdir+"Glomma_clay_drift_20120201_to_20120501.nc"
        self.sediment_organizer.create_output_filenames()

        self.assertEqual(expected, self.sediment_organizer.confobj.outputFilename)


if __name__ == "__main__":
    unittest.main()
