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

    def test_generate_densities_returns_correct_range(self):
        min_d=100
        max_d=200
        mean_d=150
        std_d=50/3.

        densities_p = self.sediment_organizer.confobj.generate_gaussian_distribution(mean_d, std_d,
                                                                                     self.sediment_organizer.confobj.number_of_particles)

        self.assertTrue(np.all(densities_p > 0))
        self.assertTrue((min_d < np.mean(densities_p)) and (np.mean(densities_p) < max_d))

    # The values of densities for sand and
    # clay are taken from literature while the diameters are taken from observations
    # done in Glomma June 2020. Particle sizes ranged from 0.0002 - 0.2 mm
    def test_terminal_velocity_calculation(self):

        diameters_p = self.sediment_organizer.confobj.generate_gaussian_distribution(0.006546e-3, 0.001e-3/3.,
                                                             self.sediment_organizer.confobj.number_of_particles)
        densities_p = self.sediment_organizer.confobj.generate_gaussian_distribution(1500, 500/3.,
                                                             self.sediment_organizer.confobj.number_of_particles)

        T0 = np.ones(len(diameters_p))*10.0
        S0 = np.ones(len(diameters_p))*27.0
        term_vel = self.sediment_drift.calc_terminal_velocity(densities_p, diameters_p, T0, S0)

        self.assertIsNotNone(term_vel)

    def test_terminal_velocity_calculation_positive_buoyant_particles_rise(self):
        diameters_p=np.asarray([0.006546e-3,0.006546e-3,0.006546e-3])/1000.
        densities_p=np.asarray([1000,1005,1010])

        T0 = np.ones(len(diameters_p))*10.0
        S0 = np.ones(len(diameters_p))*27.0
        term_vel = self.sediment_drift.calc_terminal_velocity(densities_p, diameters_p, T0, S0)

        self.assertIsNotNone(term_vel)
        self.assertTrue(np.all(term_vel > 0))

    def test_terminal_velocity_calculation_exact_from_Phil(self):
        # Test the setup of diameters and densities and velocities used by Phil in
        # ROMS and compare with our Stokes settlement velocities. These are cohesive particles
        diameters_p = np.asarray([0.000898e-3, 0.002424e-3, 0.006546e-3, 0.017678e-3, 0.047738e-3, 0.128917e-3, 0.348323e-3])
        densities_p = np.asarray([1981.330, 1611.396, 1313.938, 1141.585, 1064.706, 1037.335, 1029.366])

        # The settling velocities are taken from Phil for testing (mm/s)
        settling_velocities=np.asarray([0.000300, 0.001340, 0.004799, 0.013978, 0.033572, 0.067335, 0.114143])/(-1000.)
        T0 = np.ones(len(diameters_p)) * 10.0
        S0 = np.ones(len(diameters_p)) * 27.0
        term_vel = self.sediment_drift.calc_terminal_velocity(densities_p, diameters_p, T0, S0)

        self.assertIsNotNone(term_vel)
        self.assertTrue(np.all(term_vel < 0))

        np.testing.assert_allclose(settling_velocities,term_vel, atol=1e-3)

    def test_non_cohesive_terminal_velocity_calculation_exact_from_Phil(self):
        # Test the setup of diameters and densities and velocities used by Phil in
        # ROMS and compare with our Stokes settlement velocities. These are cohesive particles
        diameters_p = np.asarray(
            [6.5461e-6, 17.6777e-6, 47.7384e-6, 128.9173e-6, 348.1323e-6])
        densities_p = np.asarray([2650.0, 2650.0, 2650.0, 2650.0, 2650.0])

        # The settling velocities are taken from Phil for testing (mm/s)
        settling_velocities = np.asarray([-0.0271e-3, -0.1979e-3, -1.4433e-3, -10.5253e-3, -76.7539e-3])
        T0 = np.ones(len(diameters_p)) * 10.0
        S0 = np.ones(len(diameters_p)) * 27.0
        term_vel = self.sediment_drift.calc_terminal_velocity(densities_p, diameters_p, T0, S0)

        self.assertIsNotNone(term_vel)
        self.assertTrue(np.all(term_vel < 0))

        np.testing.assert_allclose(settling_velocities, term_vel, atol=1e-3)

    def test_terminal_velocity_calculation_negative_buoyant_particles_sink(self):
        diameters_p=np.asarray([0.006546e-3,0.006546e-3,0.006546e-3])/1000.
        densities_p=np.asarray([1035,1235,1110])

        T0 = np.ones(len(diameters_p))*10.0
        S0 = np.ones(len(diameters_p))*27.0
        term_vel = self.sediment_drift.calc_terminal_velocity(densities_p, diameters_p, T0, S0)

        self.assertIsNotNone(term_vel)
        self.assertTrue(np.all(term_vel < 0))

    def test_terminal_velocity_calculation_negative_and_postive_buoyant_particles_sink_and_rise(self):
        diameters_p=np.asarray([0.006546e-3,0.006546e-3,0.006546e-3,0.006546e-3])/1000.
        densities_p=np.asarray([1000,1006,2335,2110])

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
