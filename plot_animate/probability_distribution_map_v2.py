# coding=utf-8
 
import os, sys
import numpy as np
import numpy.ma as ma
import glob
import matplotlib
from matplotlib.pyplot import cm 
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import pandas as pd
import xarray as xr
from datetime import datetime
from netCDF4 import Dataset, date2num,num2date
from scipy.ndimage.filters import gaussian_filter
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
import animateScatter
import time
import utils
import config_bekkelaget as confm
from fast_histogram import histogram2d
import cmocean
import laplacefilter
import mpl_util
from matplotlib.pyplot import cm 
import drawCircleOfDistance
import drawBathymetry
from haversine import haversine, Unit

def createInputFilename(confobj):
    startDate=''
    if confobj.startdate.day<10:
        startDate+='0%s'%(confobj.startdate.day)
    else:
        startDate+='%s'%(confobj.startdate.day)
 
    if confobj.startdate.month<10:
        startDate+='0%s'%(confobj.startdate.month)
    else:
        startDate+='%s'%(confobj.startdate.month)
 
    startDate+='%s'%(confobj.startdate.year)
 
    endDate=''
    if confobj.enddate.day<10:
        endDate+='0%s'%(confobj.enddate.day)
    else:
        endDate+='%s'%(confobj.enddate.day)
 
    if confobj.enddate.month<10:
        endDate+='0%s'%(confobj.enddate.month)
    else:
        endDate+='%s'%(confobj.enddate.month)
 
    endDate+='%s'%(confobj.enddate.year)
  
     
    confobj.outputFilename='results/Bekkelaget_{}_drift_{}_to_{}_sinkspeed_{}_experiment_{}.nc'.format(confobj.species,
    startDate,endDate,
    abs(confobj.select_sinking_velocity),
    confobj.experiment)

    confobj.outputPlotFilename='figures/Bekkelaget_{}_drift_{}_to_{}_sinkspeed_{}_experiment_{}.png'.format(confobj.species,
    startDate,endDate,
    abs(confobj.select_sinking_velocity),
    confobj.experiment)

def get_paths(confobj):
     
    createInputFilename(confobj)
    return confobj.outputFilename
 
def create_map(confobj):
    plt.clf()
    confobj.ax = plt.subplot(111)
    mymap = Basemap(llcrnrlon=confobj.probxmin, llcrnrlat=confobj.probymin,
                    urcrnrlon=confobj.probxmax, urcrnrlat=confobj.probymax,resolution='f', 
                    projection='merc',area_thresh = 0.01)
 
  #  mymap.fillcontinents(color='lightgrey',zorder=6,alpha = 1.0)
    mymap.drawcoastlines(linewidth=0.2, linestyle='solid', color='k', antialiased=1)
    confobj.mymap=mymap
   # addGADM(confobj)
    drawBathymetry.addBathymetryROMS(confobj)

   # drawBathymetry.addBathymetry(confobj)

def addGADM(confobj):
    gadmfile='/Users/trondkr/Dropbox/NIVA/Bekkelaget-microplast/gadm36_NOR_shp/gadm36_NOR_0'
    info = confobj.mymap.readshapefile(gadmfile, 'comarques')
    print(info)

def find_depth(data):
    data['z'] = data['z'] * -1.
    # ! find first non nan at first and cut the rest 
    data = data.where(data.z != np.nan)
    data = data.where(data.sea_floor_depth_below_sea_level != 'nan',drop = True)
    # find differences between floor depth and particle depth for each trajectory
    data['dif_depth'] =  data.sea_floor_depth_below_sea_level - data.z 
    return data

def get_start(d,n):
    # find index of the release event, 
    # first non masked element
    arr = np.ma.masked_invalid(d.dif_depth[n].values)
    if arr.count() == 0:
        return None
    return np.ma.flatnotmasked_edges(arr)[0]

def get_sed(confobj,d,n,start = None):
   
    if start == None:
        start = get_start(d,n)
    # find index in array of sedimentations time 
    # first time when difference between seafloor 
    # mask non-sedimented particles
    arr = np.ma.masked_greater(d.dif_depth[n].values[start:],confobj.sed_crit)   
    if arr.count() == 0:
        return None
    return np.ma.flatnotmasked_edges(arr)[0]
    
def get_pos(confobj):     
    print("Opening file {}".format(confobj.paths)) 
    df = xr.open_mfdataset(confobj.paths, concat_dim='trajectory') 

    d = df.groupby(df.trajectory).apply(find_depth) #.sel(time=slice(confobj.startdate, confobj.enddate))
    parts = range(0,len(d.trajectory)-1)
    indexes=[]
    print("Number of trajectories {}".format(len(parts)))
    indexes = [get_sed(confobj,d,n) for n in parts]
   
    lons=[]; lats=[]; z=[]; time=[]
    for i,index in enumerate(indexes):
        if index is not None:
            print("Running trajectory {} sediment index {}".format(i,index))
            lons.append(d.lon[i,index].values)  
            lats.append(d.lat[i,index].values)
            z.append(d.z[i,index].values)
            time.append(d.time[index].values)    

    return np.array([np.array(xi) for xi in lats]), np.array([np.array(xi) for xi in lons]), np.array([np.array(xi) for xi in z]), np.array([np.array(xi) for xi in time])

def createBins(confobj):
 
    print('func: createBins() => Creating bins for averaging')
    
    dy = haversine((confobj.probymin,confobj.probxmin),(confobj.probymax,confobj.probxmin))
    dx = haversine((confobj.probymin,confobj.probxmin),(confobj.probymin,confobj.probxmax))

    print("Distance from minimum to maximim longitude binned area is %s km"%(dx))
    print("Distance from minimum to maximim latitude binned area is %s km"%(dy))

    nx=int(abs(dx/confobj.requiredResolution))
    ny=int(abs(dy/confobj.requiredResolution))
    print("nx {} ny {}".format(nx,ny))

    confobj.lon_bins = np.linspace(np.floor(confobj.xmin),np.ceil(confobj.xmax),nx,endpoint=True) 
    confobj.dx=len(confobj.lon_bins)
    print("DELTA X = {}".format(confobj.lon_bins))
 
    confobj.lat_bins = np.linspace(np.floor(confobj.ymin),np.ceil(confobj.ymax),ny,endpoint=True) 
    print("DELTA Y = {}".format(confobj.lat_bins))
    confobj.dy=len(confobj.lat_bins)
     
    print('=> created binned array of domain of grid cell size (%s,%s) with resolution %s'%(confobj.deltaX,confobj.deltaY,confobj.requiredResolution))
     
def get_density(lats, lons, nlevels, confobj):
 
   # XX=np.ma.masked_where(lons>200, lons)
   # YY=np.ma.masked_where(lats>200, lats)
    density, xedges, yedges = np.histogram2d(lons.flatten(), lats.flatten(), 
                                            range=[[confobj.probxmin,confobj.probxmax],
                                            [confobj.probymin,confobj.probymax]], 
                                            bins=[confobj.dx,confobj.dy])
    
    total = np.sum(density)
    density=(density/total)*100.
     
    print("Total number of points {} percentage sum {}".format(total,np.sum(density)))
    density = ma.masked_where(density == 0, density)
    levels = MaxNLocator(nbins=nlevels).tick_values(0.1,2)
    levels=np.arange(0.1,4,0.1)
 
    norm = BoundaryNorm(levels, ncolors=confobj.cmap.N, clip=True)
 
    density = density.T
    tox, toy = np.meshgrid(xedges, yedges)
    Xd, Yd = confobj.mymap(tox, toy)

    # Turn the lon/lat of the bins into 2 dimensional arrays 
  #  lon_bins_2d, lat_bins_2d = np.meshgrid(confobj.lon_bins, confobj.lat_bins)
   
    return Xd,Yd,density #lon_bins_2d,lat_bins_2d,density,norm

def make_map(confobj):
    create_map(confobj)
    lats,lons,depths,times = get_pos(confobj)
    
    createBins(confobj)  
    confobj.mymap.drawparallels(confobj.lat_bins,linewidth=0.2, fmt='%g'+ 'E', fontsize=5, color='gray', labels=[True,False,False,False]) 
    confobj.mymap.drawmeridians(confobj.lon_bins,linewidth=0.2, fmt='%g'+ 'E', fontsize=5, color='gray',labels=[False,False,False,True])

    confobj.results_startdate=times[0]
    confobj.results_enddate=times[-1]
    
    if confobj.plot_type == 'heatmap':
        confobj.cmap = plt.get_cmap(confobj.cmapname)
        nlevels=10
        print(np.shape(lats),np.shape(lons))
        Xd,Yd,density = get_density(lats, lons, nlevels, confobj)

        cs = confobj.mymap.pcolormesh(Xd,Yd, density, cmap=confobj.cmap, edgecolors='face',linewidths=0.1) #,alpha=0.8)  #norm=norm,
        #cs = confobj.mymap.contourf(Xd[:-1, :-1],Yd[:-1, :-1], density, cmap=confobj.cmap,levels = 50) #,edgecolors='face',linewidths=0.1) #,alpha=0.8)  #norm=norm,

        # LOKI distribution/seed area
        X,Y = drawCircleOfDistance.createCircleAroundWithRadius(confobj.st_lats[0],confobj.st_lons[0],confobj.releaseRadius/1000.)
        confobj.mymap.plot(X,Y,latlon=True,marker=None,color='y',linewidth=0.9)

        # LOKI main point
        x,y = confobj.mymap(confobj.st_lons[0], confobj.st_lats[0])
        confobj.mymap.plot(x,y ,marker='D',color='r',markersize=0.4)

        plt.colorbar(cs, shrink=0.7)

    elif confobj.plot_type == 'scatter':
        x,y = confobj.mymap(lons,lats)
        confobj.mymap.scatter(x,y,alpha = 0.3,c = 'r',s = 1)
 
        # LOKI distribution/seed area
        X,Y = drawCircleOfDistance.createCircleAroundWithRadius(confobj.st_lats[0],confobj.st_lons[0],confobj.releaseRadius/1000.)
        confobj.mymap.plot(X,Y,latlon=True,marker=None,color='b',linewidth=0.2)
 
        # LOKI main point
        x,y = confobj.mymap(confobj.st_lons[0], confobj.st_lats[0])
        confobj.mymap.plot(x,y ,marker='D',color='b',markersize=0.2)
        plt.colorbar(cs, shrink=1.0)

    print("Printing figure to filee {} ".format(confobj.outputPlotFilename))
    plt.savefig(confobj.outputPlotFilename,format = 'png',dpi = 300)
 
 
 
def call_make_map(confobj):
     
    confobj.paths = get_paths(confobj) 
    make_map(confobj)
 
if __name__ == "__main__":
    start_time = time.time()
    experiments = [0,1]
    years=[2019]
    for experiment in experiments:
        confobj=confm.bekkelaget_conf(experiment)
     
        for year in years:
            
            confobj.startdate=datetime(year,7,1,12,0,0)
            confobj.enddate=datetime(year,7,7,18,0,0)
            marine_organism="microplast"
    
            for confobj.select_sinking_velocity in confobj.sinkingvelocities:
                confobj.experiment=experiment
                confobj.species=marine_organism
                confobj.plot_type='heatmap'
                call_make_map(confobj) 