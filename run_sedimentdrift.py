from datetime import datetime, timedelta
import numpy as np
from opendrift.readers import reader_basemap_landmask
from opendrift.readers import reader_ROMS_native
from opendrift.models.plastdrift_bekkelaget import PlastDrift
import logging
import os
from netCDF4 import Dataset, date2num, num2date
from numpy.random import RandomState
import matplotlib.pyplot as plt
import time
import config_bekkelaget as confm
import random
import logging

__author__ = 'Trond Kristiansen'
__email__ = 'me (at) trondkristiansen.com'
__created__ = datetime(2020, 6, 29)
__modified__ = datetime(2020, 6, 29)
__version__ = "1.0"
__status__ = "Development, modified on 29.06.2020"


class Sediment_Organizer:

    def __init__(self):
        self.confobj = confm.martini_conf()

    def create_output_filenames(self, startDate=None, endDate=None) -> object:

        if self.confobj.startdate.day < 10:
            startDate += '0%s' % self.confobj.startdate.day
        else:
            startDate += '%s' % self.confobj.startdate.day

        if self.confobj.startdate.month < 10:
            startDate += '0%s' % self.confobj.startdate.month
        else:
            startDate += '%s' % self.confobj.startdate.month

        startDate += '%s' % self.confobj.startdate.year

        if self.confobj.enddate.day < 10:
            endDate += '0%s' % self.confobj.enddate.day
        else:
            endDate += '%s' % self.confobj.enddate.day

        if self.confobj.enddate.month < 10:
            endDate += '0%s' % self.confobj.enddate.month
        else:
            endDate += '%s' % self.confobj.enddate.month

        endDate += '%s' % self.confobj.enddate.year

        outputFilename = self.confobj.outputdir + '/Glomma_{}_drift_{}_to_{}.nc'.format(self.confobj.species,
                                                                                        startDate,
                                                                                        endDate)

        if os.path.exists(outputFilename):
            os.remove(outputFilename)
        self.confobj.outputFilename = outputFilename
        logging.debug("Result files will be stored as:\nnetCDF=> {}".format(self.confobj.outputFilename))

    def create_and_run_simulation(self):
        # Setup a new simulation
        o = SedimentDrift(loglevel=0)  # Set loglevel to 0 for debug information

        reader_physics = reader_ROMS_native.Reader(self.confobj.basedir + self.confobj.pattern)
        o.add_reader([reader_physics])

        #######################
        # Adjusting configuration
        #######################
        o.set_config('processes:turbulentmixing', True)
        o.set_config('processes:verticaladvection', True)
        o.set_config('turbulentmixing:diffusivitymodel', 'gls_tke')
        o.set_config('turbulentmixing:TSprofiles', True)
        # o.set_config('turbulentmixing:mixingmodel','randomwalk')
        o.set_config('drift:scheme', 'runge-kutta4')
        o.set_config('general:coastline_action', 'previous')
        o.set_config('general:basemap_resolution', 'f')
        o.set_config('drift:lift_to_seafloor', True)

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
                                                                self.confobj.startdate,
                                                                self.confobj.enddate))
        o.seed_elements(lon=self.confobj.st_lons,
                        lat=self.confobj.st_lats,
                        number=self.confobj.releaseParticles,
                        radius=[self.confobj.releaseRadius],
                        cone=False,
                        time=[self.confobj.startdate, self.confobj.enddate],
                        terminal_velocity=self.confobj.sinkingvelocities[self.confobj.experiment],
                        z=z_levels)

        print('Elements scheduled for {} : {}'.format(self.confobj.species, o.elements_scheduled))

        o.run(end_time=self.confobj.enddate,
              time_step=timedelta(minutes=30),
              time_step_output=timedelta(minutes=30),
              outfile=self.confobj.outputFilename,
              export_variables=['sea_floor_depth_below_sea_level', 'z', 'terminal_velocity', 'diameter'])

    def start_simulations(self):
        start_time = time.time()

        experiments = [0]  # Used as index other places so have to run from 0---N
        years = [2019]

        for year in years:
            self.confobj.startdate = datetime(year, 7, 1, 12, 0, 0)
            self.confobj.enddate = datetime(year, 7, 7, 12, 0, 0)
            logging.debug(
                "Running experiment for period {} to {}".format(self.confobj.startdate.year, self.confobj.enddate))

            for self.confobj.select_sinking_velocity in self.confobj.sinkingvelocities:

                self.create_output_filenames(self.confobj)

                self.create_and_run_simulation(self.confobj)

        logging.debug("---  It took %s seconds to run the script ---" % (time.time() - start_time))


def main():
    run = Sediment_Organizer()
    run.start_simulations()


if __name__ == '__main__':
    main()
