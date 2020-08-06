import matplotlib.animation as animation
import matplotlib.patches as mpatches
import matplotlib.path as mpath
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.collections import PatchCollection
import cartopy.feature as cfeature
import config_plot
import bathymetry

class KelpPolygons(object):

    def __init__(self, mymap, ax, fill=False):
        self.shapefile = '/Users/trondkr/Dropbox/NIVA/KelpFloat/Kelp/Shapefile/Shapefile05112018/kelpExPol_11sept2018.shp'
        self.mymap = mymap
        self.ax = ax
        self.fill = fill

    #  self.add_polygons_to_map()

    def getPathForPolygon(self, ring):
        codes = []
        x = [ring.GetX(j) for j in range(ring.GetPointCount())]
        y = [ring.GetY(j) for j in range(ring.GetPointCount())]

        codes += [mpath.Path.MOVETO] + (len(x) - 1) * [mpath.Path.LINETO]

        pathX, pathY = self.mymap(x, y)
        mymappath = mpath.Path(np.column_stack((pathX, pathY)), codes)

        return mymappath

    def createPathsForPolygons(self):
        # Returns a list of all the patches (polygons) in the Shapefile
        mypatches = []
        s = ogr.Open(self.shapefile)

        for layer in s:

            # get projected spatial reference
            sr = layer.GetSpatialRef()
            # get geographic spatial reference
            geogr_sr = sr.CloneGeogCS()
            # define reprojection
            proj_to_geog = osr.CoordinateTransformation(sr, geogr_sr)

            polygons = [x + 1 for x in range(layer.GetFeatureCount() - 1)]
            for polygonIndex, polygon in enumerate(polygons):

                feature = layer.GetFeature(polygonIndex)
                geom = feature.GetGeometryRef()

                ring = geom.GetGeometryRef(0)
                geom.Transform(proj_to_geog)

                if ring.GetPointCount() > 3:
                    print("Looping over polygon index {} with {} points".format(polygonIndex, ring.GetPointCount()))
                    polygonPath = self.getPathForPolygon(ring)
                    fillcolor = 'red' if self.fill else 'None'
                    path_patch = mpatches.PathPatch(polygonPath, lw=2, edgecolor="black", facecolor='red')
                    mypatches.append(path_patch)
            return mypatches

    def add_polygons_to_map(self):
        mypatches = []
        print("Adding polygons to plot from file {}".format(self.shapefile))
        mypatches = self.createPathsForPolygons()

        print("Plotting {} patches".format(len(mypatches)))
        p = PatchCollection(mypatches,
                            alpha=1.0)  # cmap=matplotlib.cm.RdYlBu,alpha=1.0,facecolor='red',lw=2.0,edgecolor='red',zorder=10)

        colors = 100 * np.random.rand(len(mypatches))
        p = PatchCollection(mypatches, alpha=0.7)
        p.set_array(np.array(colors))
        self.ax.add_collection(p)


class AnimatedScatter():
    """An animated scatter plot using matplotlib.animations.FuncAnimation."""


    def __init__(self, lons, lats, z, time, output_filename):
        self.z = z
        self.lons = lons
        self.lats = lats
        self.time = time
        self.output_filename=output_filename
        self.scat=None
        self.ttl=None
        self.config=config_plot.ConfigPlot()

        Writer = animation.writers['ffmpeg']
        self.writer = Writer(fps=15, metadata=dict(artist='Trond.Kristiansen@niva.no'), bitrate=1800)

        bath = bathymetry.Bathymetry(self.config)
        bath.add_bathymetry_from_etopo1()

        # polygons = KelpPolygons(self.ax)

        # Setup the animation with init function and update function
        frame_length = len(self.z[0, :]) - 1
        self.ani = animation.FuncAnimation(plt.gcf(),
                                           self.update,
                                           interval=10,
                                           frames=frame_length,
                                           init_func=self.initialize_plot,
                                           blit=False)

    def initialize_plot(self):
        """Initial drawing of the scatter plot."""

        self.scat = self.config.ax.scatter(self.lons[0, 0], self.lats[0, 0], c=self.z[0,0]
                                   #  , vmax=self.vmax
                                   #  , vmin=self.vmin
                                     # ,cmap='coolwarm'
                                   #  , norm=LogNorm()
                                     , transform=self.config.projection, edgecolor='none', s=0.6)
        cbar = plt.colorbar(self.scat)
   #     cbar.set_label('Melt water Flux (mm/yr)')

        self.ttl = self.config.ax.text(1.5, 1.05, '', transform=self.config.ax.transAxes, va='center')

        return self.scat

    def save_animation(self):
        self.ani.save(self.output_filename, writer=self.writer)

    def update(self, i):
        """Update the scatter plot."""
        print("progress {}".format(i))
        self.scat.remove()
      #  data = (np.c_[np.squeeze(self.lons[:, i]), np.squeeze(self.lats[:, i])])
        colors = plt.cm.viridis(self.z[:,i])
        self.scat = self.config.ax.scatter(self.lons[:, i], self.lats[:, i], marker="o",
                                   facecolors=colors, s=4,
                                    transform=self.config.projection, edgecolor='none')

        date_object = self.time[i]
        d = pd.to_datetime(date_object)
        plt.title('{}.{}.{} {}:{}'.format(d.year, d.month, d.day, d.hour, d.minute))

        return self.scat


if __name__ == '__main__':
    a = AnimatedScatter("test.mp4")

