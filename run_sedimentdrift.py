import logging
import time
from datetime import datetime, timedelta

from opendrift.readers import reader_ROMS_native

from config_sedimentdrift import MartiniConf
from sedimentdrift import SedimentDrift

__author__ = 'Trond Kristiansen'
__email__ = 'me (at) trondkristiansen.com'
__created__ = datetime(2020, 6, 29)
__modified__ = datetime(2020, 7, 20)
__version__ = "1.0"
__status__ = "Development, modified on 29.06.2020, 20.07.2020"


class Sediment_Organizer:

    def __init__(self):
        print("Inside init for sediment organizer")
        self.confobj: MartiniConf = MartiniConf()

    # Setup the sediment object and configuration
    def setup_and_config_sediment_module(self) -> SedimentDrift:
        # Setup a new simulation
        o = SedimentDrift(loglevel=self.confobj.debug)  # Set loglevel to 0 for debug information
        o.set_config('drift:vertical_mixing', True)
        o.set_config('drift:vertical_advection', True)
        o.set_config('vertical_mixing:diffusivitymodel', 'gls_tke')
        o.set_config('vertical_mixing:TSprofiles', False)
     #   o.set_config('drift:scheme', 'runge-kutta4')
        o.set_config('drift:lift_to_seafloor', True)
        o.set_config('vertical_mixing:update_terminal_velocity', True)
        o.set_config('drift:current_uncertainty', .2)
        o.set_config('drift:wind_uncertainty', 2)
        o.set_config('vertical_mixing:diffusivitymodel', 'windspeed_Large1994')

        return o

    def create_and_run_simulation(self):
        o = self.setup_and_config_sediment_module()
        reader_physics = reader_ROMS_native.Reader(self.confobj.datadir + self.confobj.pattern)
        o.add_reader([reader_physics])

        logging.debug("Releasing {} sediments between {} and {}".format(self.confobj.species,
                                                                        self.confobj.start_date,
                                                                        self.confobj.end_date))
        o.seed_elements(lon=self.confobj.st_lons,
                        lat=self.confobj.st_lats,
                        number=self.confobj.number_of_particles,
                        radius=[self.confobj.release_radius],
                        cone=False,
                        diameter=self.confobj.diameters,
                        density=self.confobj.densities,
                        time=[self.confobj.start_date, self.confobj.end_date],
                        z=self.confobj.init_release_depths())

        logging.debug('Elements scheduled for {} : {}'.format(self.confobj.species, o.elements_scheduled))

        o.run(end_time=self.confobj.end_date,
              time_step=timedelta(minutes=10),
              time_step_output=timedelta(minutes=10),
              outfile=self.confobj.outputFilename,
              export_variables=['sea_floor_depth_below_sea_level', 'z', 'diameter', 'density','terminal_velocity'])

        o.animation(color='z', fast=False, buffer=.01, filename="test.mp4")
       # o.plot_property('z', filename="test.png")

        o.animation_profile(filename="test.mp4")

    def start_simulations(self):
        start_time = time.time()

        logging.debug("Running experiment for period {} to {}". \
                      format(self.confobj.start_date.year, self.confobj.end_date))

        self.confobj.create_output_filenames()
        self.create_and_run_simulation()

        logging.debug("---  It took %s seconds to run the script ---" % (time.time() - start_time))


def main():
    run = Sediment_Organizer()
    run.start_simulations()


if __name__ == '__main__':
    main()
