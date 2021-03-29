#
#
# Config object for MARTINI sediment drift
import logging
import os
import random
import time
from datetime import datetime
from typing import List

import numpy as np

__author__ = 'Trond Kristiansen'
__email__ = 'Trond.Kristiansen (at) niva.no'
__created__ = datetime(2020, 6, 29)
__modified__ = datetime(2020, 8, 10)
__version__ = "1.0"
__status__ = "Development, modified on 29.06.2020, 16.07.2020, 10.08.2020"

"""
https://www.fondriest.com/environmental-measurements/parameters/hydrology/sediment-transport-deposition/
"""


class MartiniConf():

    def __init__(self):
        print('\n--------------------------\n')
        print('Started ' + time.ctime(time.time()))
        self.debug = True
        self.start_date: datetime = datetime(2019, 1, 1)
        self.end_date: datetime = datetime(2019, 12, 30)
        self.outputdir = None
        self.verticalBehavior = False
        self.basedir = '/cluster/projects/nn9297k/Glomma_particles/'
        self.datadir = "/cluster/projects/nn9197k/physics/"
        self.outputdir = self.basedir + 'output/'
        self.pattern = 'martini_800m_his_'
        self.species = 'clay'
        self.selectyear = 'all'

        # Glomma - seed locations
        self.st_lons = [10.962920]
        self.st_lats = [59.169194]
        self.number_of_particles = 600
        self.release_radius = 600
        # diameter in meter, densities in kg/m3

        self.diameters = self.generate_uniform_distribution(6.5461e-6, 348.1323e-6, self.number_of_particles)
        self.densities = np.flip(self.generate_uniform_distribution(2600, 2650, self.number_of_particles), axis=0)

        self.outputFilename = None
        self.results_startdate = None
        self.results_enddate = None

    def generate_uniform_distribution(self, part_min, part_max, number):
        # Diameters in meter
        dist = np.asarray(
            [random.uniform(part_min, part_max) for i in range(number)])
        return np.where(dist < 0, 0.0001e-12, dist)

    def generate_gaussian_distribution(self, part_mean, part_std, number):
        # Diameters in meter
        dist = np.asarray(
            [random.gauss(part_mean, part_std) for i in range(number)])
        return np.where(dist < 0, 0.0001e-12, dist)

    def create_output_filenames(self):
        start_date_str: str = '{}{}{}'.format(str(self.start_date.year),
                                              str(self.start_date.month).zfill(2),
                                              str(self.start_date.day).zfill(2))

        end_date_str: str = '{}{}{}'.format(str(self.end_date.year),
                                            str(self.end_date.month).zfill(2),
                                            str(self.end_date.day).zfill(2))

        self.outputFilename = self.outputdir + 'Glomma_{}_drift_{}_to_{}.nc'.format(self.species,
                                                                                    start_date_str,
                                                                                    end_date_str)

        if os.path.exists(self.outputFilename):
            os.remove(self.outputFilename)

        logging.debug("Result files will be stored as:\nnetCDF=> {}".format(self.outputFilename))

        # Initialize release depths

    def init_release_depths(self) -> List[str]:
        if not os.path.exists(self.outputdir): os.mkdir(self.outputdir)

        # Spread particles/sediments usin   g a Gauss shape in the upper surface
        low_depth, mean_depth, high_depth = -0.05, -0.01, 0
        stdev = (low_depth - mean_depth) / 3.
        z_levels = []
        while len(z_levels) < self.number_of_particles:
            sample = random.gauss(mean_depth, stdev)
            if low_depth <= sample < high_depth:
                z_levels.append(sample)
            else:
                z_levels.append(mean_depth)

        print('Seeding {} elements within a radius of {} m (depths {} to {} m)'.format(self.number_of_particles,
                                                                                       self.number_of_particles,
                                                                                       np.min(z_levels),
                                                                                       np.max(z_levels)))
        return z_levels
