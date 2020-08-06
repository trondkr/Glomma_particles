
import numpy as np
from datetime import datetime
import matplotlib
import pylab as pl
import cartopy.crs as ccrs
import cartopy
import cartopy.feature as cfeature
import matplotlib.pyplot as plt

__author__ = 'Trond Kristiansen'
__email__ = 'Trond.Kristiansen (at) niva.no'
__created__ = datetime(2020, 8, 5)
__modified__ = datetime(2020, 8, 5)
__version__ = "1.0"
__status__ = "Development, modified on 05.08.2020"


class ConfigPlot():

    def __init__(self):
        # Define the longitude/latitude boundaries of the plot or animation
        self.xmin = 10.55
        self.xmax = 11.3
        self.ymin = 58.8
        self.ymax = 59.35
        self.ROMSFILE = None
        self.projection = ccrs.PlateCarree()

        self.etopo1 = '/Users/trondkr/Dropbox/NIVA/Farallon/QIN/oceanography/ETOPO1/ETOPO1_Ice_g_gmt4.grd'

        # add coastlines from GSHHS
        shpfile = cartopy.io.shapereader.gshhs('f')

        shp = cartopy.io.shapereader.Reader(shpfile)
        rivers_10m = cfeature.NaturalEarthFeature('physical', 'rivers_lake_centerlines', '10m')

        # Axes and properties
        self.ax = plt.axes(projection=self.projection)
        self.ax.gridlines()
        self.ax.set_extent(self.get_map_extent(), self.projection)

        self.ax.add_geometries(
            shp.geometries(), ccrs.PlateCarree(), edgecolor='black', facecolor='lightgrey', linewidth=0.2)

        self.ax.add_feature(cfeature.LAKES, edgecolor='black')
        self.ax.add_feature(cfeature.RIVERS, edgecolor='black')
      #  self.ax.add_feature(rivers_10m, facecolor=cfeature.COLORS['water'],
      #                      edgecolor=cfeature.COLORS['water'])



    def get_map_extent(self):
        return [self.xmin, self.xmax, self.ymin, self.ymax]

    def level_colormap(self, levels, cmap=None):
        """Make a colormap based on an increasing sequence of levels"""

        # Start with an existing colormap
        if cmap == None:
            cmap = pl.get_cmap()

        # Spread the colours maximally
        nlev = len(levels)
        S = np.arange(nlev, dtype='float') / (nlev - 1)
        A = cmap(S)

        # Normalize the levels to interval [0,1]
        levels = np.array(levels, dtype='float')
        L = (levels - levels[0]) / (levels[-1] - levels[0])

        # Make the colour dictionary
        R = [(L[i], A[i, 0], A[i, 0]) for i in range(nlev)]
        G = [(L[i], A[i, 1], A[i, 1]) for i in range(nlev)]
        B = [(L[i], A[i, 2], A[i, 2]) for i in range(nlev)]
        cdict = dict(red=tuple(R), green=tuple(G), blue=tuple(B))

        # Use
        return matplotlib.colors.LinearSegmentedColormap(
            '%s_levels' % cmap.name, cdict, 256)
