import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from matplotlib.pyplot import cm 
from mpl_toolkits.basemap import Basemap
import matplotlib.path as mpath
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection
import animateScatter
import laplacefilter
import mpl_util
import xarray as xr
import config_bekkelaget as confm
import drawCircleOfDistance
import drawBathymetry

class Tracks(object):
    """An animated scatter plot using matplotlib.animations.FuncAnimation."""
    def __init__(self,lons,lats,z,confobj):
     
        self.z = z
        plt.clf()
        self.ax = plt.subplot(111)
        self.mymap = Basemap(llcrnrlon=confobj.probxmin, llcrnrlat=confobj.probymin,
                        urcrnrlon=confobj.probxmax, urcrnrlat=confobj.probymax, resolution='f',
                        projection='merc', area_thresh=0.01)

        #  mymap.fillcontinents(color='lightgrey',zorder=6,alpha = 1.0)
        self.mymap.drawcoastlines(linewidth=0.2, linestyle='solid', color='k', antialiased=1)

       # self.mymap.shadedrelief()
        self.mymap.fillcontinents(color='#b8a67d',zorder=2)
        self.mymap.drawcoastlines(linewidth=0.2, linestyle='solid', color='k', antialiased=1)

       # self.addBathymetry(confobj)
        animateScatter.KelpPolygons(self.mymap,self.ax)
       
        self.x,self.y=self.mymap(lons,lats)
        confobj.mymap = self.mymap
        drawBathymetry.addBathymetryROMS(confobj)


    def plot_tracks(self,confobj):

        for traj_index in range(len(self.x[:,0])):
        #    print("Plotting trajectory {}".format(traj_index))
            self.mymap.plot(self.x[traj_index,:],self.y[traj_index],c='k',alpha=0.5,linewidth=0.4)

         # distribution/seed area
        X,Y = drawCircleOfDistance.createCircleAroundWithRadius(confobj.st_lats[0],confobj.st_lons[0],confobj.releaseRadius/1000.)
        confobj.mymap.plot(X,Y,latlon=True,marker=None,color='y',linewidth=0.9)

        # main point
        x,y = confobj.mymap(confobj.st_lons[0], confobj.st_lats[0])
        confobj.mymap.plot(x,y ,marker='D',color='r',markersize=0.4)
        

        plt.savefig(confobj.outputPlotFilename,format = 'png',dpi = 300)