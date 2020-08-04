import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from matplotlib.pyplot import cm
import sys
import matplotlib.path as mpath
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection
from mpl_toolkits.axes_grid1 import make_axes_locatable
import pandas as pd
import config_bekkelaget as confm


class KelpPolygons(object):

    def __init__(self,mymap,ax,fill=False):
        self.shapefile = '/Users/trondkr/Dropbox/NIVA/KelpFloat/Kelp/Shapefile/Shapefile05112018/kelpExPol_11sept2018.shp'
        self.mymap=mymap
        self.ax=ax
        self.fill=fill
      #  self.add_polygons_to_map()
       
    def getPathForPolygon(self,ring):
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
                    fillcolor='red' if self.fill else 'None'
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
    def __init__(self,lons,lats,z,time,confobj):
     
        self.z = z
        self.time=time
  
        Writer = animation.writers['ffmpeg']
        self.writer = Writer(fps=15, metadata=dict(artist='Trond.Kristiansen@niva.no'), bitrate=1800)

        # Setup the figure and axes...
        self.llcrnrlon=confobj.xmin
        self.llcrnrlat=confobj.ymin
        self.urcrnrlon=confobj.xmax
        self.urcrnrlat=confobj.ymax
        
        self.fig, self.ax = plt.subplots(figsize=(10,10))
        self.mymap = Basemap(self.llcrnrlon, self.llcrnrlat,self.urcrnrlon, self.urcrnrlat,resolution=confobj.mapresolution,projection='merc')
    #    self.mymap.shadedrelief()
       # self.mymap.fillcontinents(color='#b8a67d',zorder=2)
        self.mymap.drawcoastlines(linewidth=0.2, linestyle='solid', color='k', antialiased=1)

       # polygons = KelpPolygons(self.mymap,self.ax)

        self.x,self.y=self.mymap(lons,lats)
      
        # Then setup FuncAnimation.
        framelength=len(self.z[0,:])-1
        self.ani = animation.FuncAnimation(self.fig, self.update, interval=10,frames=framelength, 
                                          init_func=self.setup_plot, blit=False)


    def setup_plot(self):
        """Initial drawing of the scatter plot."""
        
        x, y, c = (np.c_[self.x[:,0], self.y[:,0], self.z[:,0]]).T
        self.scat = self.mymap.scatter(x, y, c=c, s=15,
                                    cmap="ocean", edgecolor="k")
        self.ttl = self.ax.text(1.5, 1.05, '', transform = self.ax.transAxes, va='center')

        divider = make_axes_locatable(self.ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)

        plt.colorbar(self.scat, cax=cax)
        # For FuncAnimation's sake, we need to return the artist we'll be using
        # Note that it expects a sequence of artists, thus the trailing comma.
        return self.scat

    def saveAnim(self,confobj):
        self.ani.save(confobj.figname,writer=self.writer)

    def update(self, i):
        """Update the scatter plot."""
        data = (np.c_[np.squeeze(self.x[:,i]), np.squeeze(self.y[:,i])])
        dateobject=self.time[i]
        d = pd.to_datetime(dateobject)
        plt.title('{}.{}.{} {}:{}'.format(d.year,d.month,d.day,d.hour,d.minute))

        print("Updating frame {} for data {}".format(i,np.shape(data)))
        # Set x and y data...
        self.scat.set_offsets(data)

        # Set sizes...
      #  self.scat.set_sizes(20)
        # Set colors..
        self.scat.set_array(self.z[:,i])

        # We need to return the updated artist for FuncAnimation to draw..
        # Note that it expects a sequence of artists, thus the trailing comma.
        return self.scat


if __name__ == '__main__':
    a = AnimatedScatter("test.mp4")
   # plt.show()