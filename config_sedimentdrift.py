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
__modified__ = datetime(2020, 7, 16)
__version__ = "1.0"
__status__ = "Development, modified on 29.06.2020, 16.07.2020"

"""
https://www.fondriest.com/environmental-measurements/parameters/hydrology/sediment-transport-deposition/
"""


class MartiniConf():

    def __init__(self):
        print('\n--------------------------\n')
        print('Started ' + time.ctime(time.time()))
        self.debug = True
        self.start_date: datetime = datetime(2019, 5, 1)
        self.end_date: datetime = datetime(2019, 5, 8)
        self.outputdir = None
        self.verticalBehavior = False
        self.basedir = '/cluster/projects/nn9297k/Glomma_particles/'
        self.datadir = "/cluster/projects/nn9197k/kaihc/Run/"
        self.outputdir = self.basedir + 'output/'
        self.pattern = 'martini_800m_his_085*'
        self.species = 'clay'
        self.selectyear = 'all'

        # Glomma - seed locations
        self.st_lons = [10.962920]
        self.st_lats = [59.169194]
        self.number_of_particles = 10000
        self.release_radius = 50
        # diameter in meter, densities in kg/m3
        self.diameters = self.generate_gaussian_distribution(0.002e-3, 0.2e-3, 0.02e-3, 0.002e-3, self.number_of_particles)
        self.densities = self.generate_gaussian_distribution(1.0, 2.0, 1.5, 0.5, self.number_of_particles)
        self.sed_crit = 0.1

        self.outputFilename = None
        self.results_startdate = None
        self.results_enddate = None

    def setup_plot_conf(self):
        # For plotting
        self.requiredResolution = 0.1  # km between bins
        self.xmin = 10.475
        self.xmax = 10.85
        self.ymin = 59.6
        self.ymax = 59.95
        self.ROMSFILE = self.datadir + "martini_800m_his_0626.nc"

        self.probxmin = 10.70
        self.probxmax = 10.78
        self.probymin = 59.87
        self.probymax = 59.90

        self.plot_type = 'scatter'
        self.cmapname = 'RdYlBu_r'

        self.paths = None
        self.mymap = None
        self.ax = None
        self.deltaX = None
        self.deltaY = None
        self.dx = None
        self.dy = None
        self.cmap = None

    def generate_gaussian_distribution(self, part_min, part_max, part_mean, part_std, number):
        # Diameters in meter
        return np.asarray(
            [max(part_max, min(part_min, random.gauss(part_mean, part_std))) / 1000. for i in
             range(number)])

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

        # Spread particles/sediments using a Gauss shape in the upper surface
        low_depth, mean_depth, high_depth = -2, -0.5, 0
        stdev = (low_depth - mean_depth) / 3.
        z_levels = []
        while len(z_levels) < self.number_of_particles:
            sample = random.gauss(self.mean_depth, stdev)
            if low_depth <= sample < high_depth:
                z_levels.append(sample)
            else:
                z_levels.append(mean_depth)

        print('Seeding {} elements within a radius of {} m (depths {} to {} m)'.format(self.number_of_particles,
                                                                                       self.number_of_particles,
                                                                                       np.min(z_levels),
                                                                                       np.max(z_levels)))
        return z_levels
