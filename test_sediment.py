import unittest
import run_sedimentdrift
from datetime import datetime
from config_sedimentdrift import MartiniConf
from sedimentdrift import SedimentDrift
import numpy as np

class TestGLOMMA_init(unittest.TestCase):

    def setUp(self):
        super(TestGLOMMA_init, self).setUp()
        self.sediment_organizer = run_sedimentdrift.Sediment_Organizer()
        self.sediment_organizer.confobj.start_date = datetime(2012, 2, 1)
        self.sediment_organizer.confobj.end_date = datetime(2012, 5, 1)
        self.sediment_organizer.confobj.species = "clay"

        self.sediment_drift = SedimentDrift()

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

    def test_density_of_water_at_reference_values(self):
        T=0.0; S=35.0
        self.assertAlmostEqual(1028.10, self.sediment_drift.sea_water_density(T, S), places=1)

    # The values of densities for sand and
    # clay are taken from literature while the diameters are taken from observations
    # done in Glomma June 2020. Particle sizes ranged from 0.0002 - 0.2 mm
    def test_terminal_velocity_calculation(self):

        diameters_p = self.sediment_organizer.confobj.generate_gaussian_distribution(0.002e-3, 0.2e-3, 0.02e-3, 0.002e-3,
                                                             self.sediment_organizer.confobj.number_of_particles)
        densities_p = self.sediment_organizer.confobj.generate_gaussian_distribution(1.0, 2.0, 1.5, 0.5,
                                                             self.sediment_organizer.confobj.number_of_particles)

        T0 = np.ones(len(diameters_p))*10.0
        S0 = np.ones(len(diameters_p))*27.0
        term_vel = self.sediment_drift.calc_terminal_velocity(densities_p, diameters_p, T0, S0)
        self.assertIsNotNone(term_vel)

    def test_terminal_velocity_calculation_positive_buoyant_particles_rise(self):
        diameters_p=np.asarray([0.1,0.1,0.1])/1000.
        densities_p=np.asarray([1000,1005,1010])

        T0 = np.ones(len(diameters_p))*10.0
        S0 = np.ones(len(diameters_p))*27.0
        term_vel = self.sediment_drift.calc_terminal_velocity(densities_p, diameters_p, T0, S0)

        self.assertIsNotNone(term_vel)
        self.assertTrue(np.all(term_vel > 0))

    def test_terminal_velocity_calculation_negative_buoyant_particles_sink(self):
        diameters_p=np.asarray([0.1,0.1,0.1])/1000.
        densities_p=np.asarray([1035,1235,1110])

        T0 = np.ones(len(diameters_p))*10.0
        S0 = np.ones(len(diameters_p))*27.0
        term_vel = self.sediment_drift.calc_terminal_velocity(densities_p, diameters_p, T0, S0)

        self.assertIsNotNone(term_vel)
        self.assertTrue(np.all(term_vel < 0))

    def test_terminal_velocity_calculation_negative_and_postive_buoyant_particles_sink_and_rise(self):
        diameters_p=np.asarray([0.1,0.1,0.1,0.1])/1000.
        densities_p=np.asarray([1000,1006,1335,1110])

        T0 = np.ones(len(diameters_p))*10.0
        S0 = np.ones(len(diameters_p))*27.0
        term_vel = self.sediment_drift.calc_terminal_velocity(densities_p, diameters_p, T0, S0)

        self.assertIsNotNone(term_vel)
        self.assertFalse(np.all(term_vel < 0))
        self.assertFalse(np.all(term_vel > 0))


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
        self.sediment_organizer.confobj.create_output_filenames()

        self.assertEqual(expected, self.sediment_organizer.confobj.outputFilename)


if __name__ == "__main__":
    unittest.main()
