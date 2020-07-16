import logging
import os
import random
import time
from datetime import datetime, timedelta

import numpy as np
from opendrift.readers import reader_ROMS_native

from config_sedimentdrift import MartiniConf
from sedimentdrift import SedimentDrift

__author__ = 'Trond Kristiansen'
__email__ = 'me (at) trondkristiansen.com'
__created__ = datetime(2020, 6, 29)
__modified__ = datetime(2020, 6, 29)
__version__ = "1.0"
__status__ = "Development, modified on 29.06.2020"


class Sediment_Organizer:

    def __init__(self):
        print("Inside init for sediment organizer")
        self.confobj: MartiniConf = MartiniConf()

    def create_output_filenames(self):
        start_date_str: str = '{}{}{}'.format(str(self.confobj.start_date.year),
                                              str(self.confobj.start_date.month).zfill(2),
                                              str(self.confobj.start_date.day).zfill(2))

        end_date_str: str = '{}{}{}'.format(str(self.confobj.end_date.year),
                                            str(self.confobj.end_date.month).zfill(2),
                                            str(self.confobj.end_date.day).zfill(2))
        print(start_date_str)
        print(end_date_str)
        print(self.confobj.species)
        print(self.confobj.outputdir)

        outputFilename = self.confobj.outputdir + 'Glomma_{}_drift_{}_to_{}.nc'.format(self.confobj.species,
                                                                                       start_date_str,
                                                                                       end_date_str)

        if os.path.exists(outputFilename):
            os.remove(outputFilename)
        self.confobj.outputFilename = outputFilename
        logging.debug("Result files will be stored as:\nnetCDF=> {}".format(self.confobj.outputFilename))

    # Setup the sediment object and configuration
    def setup_and_config_sediment_module(self) -> SedimentDrift:
        # Setup a new simulation
        o = SedimentDrift(loglevel=self.confobj.debug)  # Set loglevel to 0 for debug information
        o.set_config('drift:vertical_mixing', True)
        o.set_config('drift:vertical_advection', True)
        o.set_config('vertical_mixing:diffusivitymodel', 'gls_tke')
        o.set_config('vertical_mixing:TSprofiles', True)
        o.set_config('drift:scheme', 'runge-kutta4')
        o.set_config('drift:lift_to_seafloor', True)
        o.set_config('vertical_mixing:update_terminal_velocity', True)
        return o

    def create_and_run_simulation(self):
        o = self.setup_and_config_sediment_module()
        reader_physics = reader_ROMS_native.Reader(self.confobj.basedir + self.confobj.pattern)
        o.add_reader([reader_physics])

        if not os.path.exists(self.outputdir): os.mkdir(self.outputdir)

        # Spread particles/sediments using a Gauss shape in the upper 2 meters
        low_depth, mean_depth, high_depth = -2, -0.5, 0
        stdev = (low_depth - mean_depth) / 3.
        z_levels = []
        while len(z_levels) < self.confobj.releaseParticles:
            sample = random.gauss(self.confobj.mean_depth, stdev)
            if low_depth <= sample < high_depth:
                z_levels.append(sample)
            else:
                z_levels.append(mean_depth)

        print('Seeding {} elements within a radius of {} m (depths {} to {} m)'.format(self.confobj.releaseParticles,
                                                                                       self.confobj.releaseRadius,
                                                                                       np.min(z_levels),
                                                                                       np.max(z_levels)))

        print("Releasing {} sediments between {} and {}".format(self.confobj.species,
                                                                self.confobj.start_date,
                                                                self.confobj.end_date))
        o.seed_elements(lon=self.confobj.st_lons,
                        lat=self.confobj.st_lats,
                        number=self.confobj.releaseParticles,
                        radius=[self.confobj.releaseRadius],
                        cone=False,
                        time=[self.confobj.start_date, self.confobj.end_date],
                        terminal_velocity=self.confobj.sinkingvelocities[self.confobj.experiment],
                        z=z_levels)

        print('Elements scheduled for {} : {}'.format(self.confobj.species, o.elements_scheduled))

        o.run(end_time=self.confobj.end_date,
              time_step=timedelta(minutes=30),
              time_step_output=timedelta(minutes=30),
              outfile=self.confobj.outputFilename,
              export_variables=['sea_floor_depth_below_sea_level', 'z', 'terminal_velocity', 'diameter'])

    def start_simulations(self):
        start_time = time.time()

        experiments = [0]  # Used as index other places so have to run from 0---N
        years = [2019]

        for year in years:
            self.confobj.start_date = datetime(year, 7, 1, 12, 0, 0)
            self.confobj.end_date = datetime(year, 7, 7, 12, 0, 0)
            logging.debug(
                "Running experiment for period {} to {}".format(self.confobj.start_date.year, self.confobj.end_date))

            for self.confobj.select_sinking_velocity in self.confobj.sinkingvelocities:
                self.create_output_filenames(self.confobj)

                self.create_and_run_simulation(self.confobj)

        logging.debug("---  It took %s seconds to run the script ---" % (time.time() - start_time))


def main():
    run = Sediment_Organizer()
    run.start_simulations()


if __name__ == '__main__':
    main()
