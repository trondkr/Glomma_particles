#
#
# Config object for MARTINI sediment drift
import time, calendar
from datetime import datetime, timedelta
import os
import numpy as np

__author__ = 'Trond Kristiansen'
__email__ = 'Trond.Kristiansen (at) niva.no'
__created__ = datetime(2020, 6, 29)
__modified__ = datetime(2020, 6, 29)
__version__ = "1.0"
__status__ = "Development, modified on 29.06.2020"

"""
https://www.fondriest.com/environmental-measurements/parameters/hydrology/sediment-transport-deposition/
"""
class MartiniConf():

    def __init__(self):
        print('\n--------------------------\n')
        print('Started ' + time.ctime(time.time()))
        self.debug=True

        self.paths = None
        self.mymap = None
        self.ax = None
        self.deltaX = None
        self.deltaY = None
        self.dx = None
        self.dy = None
        self.cmap = None
        self.outputFilename = None
        self.results_startdate = None
        self.results_enddate = None
        self.start_date:datetime=datetime(2000,1,1)
        self.end_date:datetime=datetime(2002,1,1)
        self.outputdir = None
        self.verticalBehavior = False
        self.basedir = '/cluster/projects/nn9297k/Glomma_particles/'
        self.outputdir = self.basedir + 'output/'
        self.pattern = 'martini_800m_his_*'
        self.species = 'clay'
        self.plot_type = 'scatter'
        self.cmapname = 'RdYlBu_r'
        self.selectyear = 'all'

        # Glomma - seed locations
        self.st_lons = [10.7528]
        self.st_lats = [59.8830]
        self.releaseParticles = 500
        self.releaseRadius = 50

        self.diameters = np.arange(0.0002, 0.2, 0.01)  # diameter in mm
        self.densities = np.arange(1.2, 1.7, 0.1)
        self.interpolation = 'linearNDFast'
        self.sed_crit = 0.1

        # For plotting
        self.requiredResolution = 0.1  # km between bins
        self.xmin = 10.475
        self.xmax = 10.85
        self.ymin = 59.6
        self.ymax = 59.95
        self.ROMSFILE = "/Users/trondkr/Dropbox/NIVA/niva_apps/fjordos_dramsfjord/grid/FjordOs_grd_v9.nc"
        self.mapresolution = 'f'

        self.probxmin = 10.70
        self.probxmax = 10.78
        self.probymin = 59.87
        self.probymax = 59.90