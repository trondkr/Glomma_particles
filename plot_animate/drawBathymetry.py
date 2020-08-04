import laplacefilter
import mpl_util
from matplotlib.pyplot import cm 
import xarray as xr
import numpy as np

def addBathymetryROMS(confobj):
        df = xr.open_mfdataset(confobj.ROMSFILE)

        bathX,bathY=confobj.mymap(df.lon_rho.values,df.lat_rho.values)
        bathZ = df.h.values
        #mask_rho = df.mask_rho.values
        levels=[-200,-175,-150,-125,-100,-75,-50,-45, -40,-30,-25,-20,-15,-10,-5]

        confobj.mymap.contourf(bathX,bathY,-bathZ,
                            cmap=mpl_util.LevelColormap(levels,cmap=cm.Greys_r),
                            alpha=0.5) 
        print("Adding bathymetry from ROMS min,mean,max depths: {},{},{}".format(np.min(bathZ),np.mean(bathZ),np.max(bathZ)))

def addBathymetry(confobj):

    etopo1='/Users/trondkr/Dropbox/NIVA/ETOPO1/ETOPO1_Ice_g_gmt4.grd'
    etopo=xr.open_dataset(etopo1)
    lats=etopo['y'].values
    lons=etopo['x'].values

    res = findSubsetIndices(confobj.ymin-5,confobj.ymax+5,confobj.xmin-40,confobj.xmax+10,lats,lons)
    res = [ int(x) for x in res ]
     
    bathy = etopo["z"][int(res[2]):int(res[3]),int(res[0]):int(res[1])].values
    bathySmoothed = laplacefilter.laplace_filter(bathy,M=None)
    lon,lat=np.meshgrid(lons[res[0]:res[1]],lats[res[2]:res[3]]) 
        
    levels=[-5000,-4000,-3000,-2000,-1750,-1500,-1250,-1000,-750,-500,-400,-300,-200,-100,-50,-10]
    x, y = confobj.mymap(lon,lat)
    etopo_contour = confobj.mymap.contourf(x,y,bathySmoothed,levels,
                       cmap=mpl_util.LevelColormap(levels,cmap=cm.Greys_r),
                       alpha=0.4,
                       origin='lower')
    
    
def findSubsetIndices(min_lat,max_lat,min_lon,max_lon,lats,lons):

    """Array to store the results returned from the function"""
    res=np.zeros((4),dtype=np.float64)
    minLon=min_lon; maxLon=max_lon

    distances1 = []; distances2 = []
    indices=[]; index=1

    for point in lats:
        s1 = max_lat-point # (vector subtract)
        s2 = min_lat-point # (vector subtract)
        distances1.append((np.dot(s1, s1), point, index))
        distances2.append((np.dot(s2, s2), point, index-1))
        index=index+1

    distances1.sort()
    distances2.sort()
    indices.append(distances1[0])
    indices.append(distances2[0])

    distances1 = []; distances2 = []; index=1

    for point in lons:
        s1 = maxLon-point # (vector subtract)
        s2 = minLon-point # (vector subtract)
        distances1.append((np.dot(s1, s1), point, index))
        distances2.append((np.dot(s2, s2), point, index-1))
        index=index+1

    distances1.sort()
    distances2.sort()
    indices.append(distances1[0])
    indices.append(distances2[0])

    """ Save final product: max_lat_indices,min_lat_indices,max_lon_indices,min_lon_indices"""
    minJ=indices[1][2]
    maxJ=indices[0][2]
    minI=indices[3][2]
    maxI=indices[2][2]

    res[0]=minI; res[1]=maxI; res[2]=minJ; res[3]=maxJ;
    return res