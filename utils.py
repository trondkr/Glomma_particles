import geopandas
import xarray as xr
import numpy as np

#criteria to find sedimentation event
sed_crit = 0.1

ranges = {1:['01052016','01082016'],2:['01032016','15052016'],
          3:['20112015','01042016'],4:['01052016','01082016'],
          5:['03082015','01082016']}

def get_polygons():
    shapefile = r'Shapefile/Shapefile05112018/kelpExPol_11sept2018.shp'
    s = geopandas.read_file(shapefile)
    return(s.index.values[2:-2] + 1)

def get_paths(polygons = None,experiment = 1):
    if polygons is None:
        polygons = get_polygons()
    elif polygons == 'All':
        polygons = get_polygons()        
    
    startdate,enddate = ranges[experiment]
    base= r'results15012019' 
    return [base+'/Kelp_polygon_%s_experiment_%s_%s_to_%s.nc' % (polygon, experiment, 
                startdate, enddate) for polygonIndex, polygon in enumerate(polygons)] 

#def is_sedimented(d,n):
#    arr = np.ma.masked_invalid(d.dif_depth[n].values)
#    s = np.ma.masked_greater(arr,sed_crit)    
#    if s.count() == 0:
#        return False
#    else: 
#        return True 

def first_n_nan(arr):

    try:
        return np.ma.flatnotmasked_edges(arr)[0]
    except:
        return None
def get_start_sed_depth(d):

    # Start - first non nan in array
    arr = np.ma.masked_invalid(d.dif_depth.values)
    start =  first_n_nan(arr)   

    # Sed - first non nan in arr where dif > 0.2 masked
    arr2 = np.ma.masked_greater(arr,sed_crit)  
    if arr2.count() == 0:
        return None,None,None
    else: 
        sed = first_n_nan(arr2) 
        sed_depth = d.z[sed].values
        return [start,sed,sed_depth]


def get_lat(d,n):
    # find lat of the particle at the sedimentation time 
    return d.lat[n][get_sed(d,n)]

def get_lon(d,n):
    # find lat of the particle at the sedimentation time 
    return d.lon[n][get_sed(d,n)]

def get_latlon(d):

    arr = np.ma.masked_invalid(d.dif_depth.values)  
    arr2 = np.ma.masked_greater(arr,sed_crit)        
    # fin lat of the particle at the sedimentation time 
    if arr2.count() == 0:
        return None
    else:    
        sed = first_n_nan(arr2) 
    return [d.lat[sed].values, d.lon[sed].values]

def get_sed_depth(d,n):
    return d.z[n][get_sed(d,n)]

def get_start(d,n):
    # find index of the release event, 
    # first non masked element
    arr = np.ma.masked_invalid(d.dif_depth[n].values)
    return first_n_nan(arr)

def get_sed(d,n,start = None):  
    if start == None:
        start = get_start(d,n)
    # find index in array of sedimentations time 
    # first time when difference between seafloor 
    # mask non-sedimented particles
    arr = np.ma.masked_greater(d.dif_depth[n].values[start:],sed_crit)    
    return first_n_nan(arr)



def get_dif_depth(data):
    # find differences between floor depth and particle depth for each trajectory     
    # ! find first non nan at first and cut the rest 
    data = data.where(data.z != 'nan')
    data = data.where(data.z != np.nan)
    data = data.where(data.sea_floor_depth_below_sea_level != 'nan',drop = True)
    data['dif_depth'] =  data.sea_floor_depth_below_sea_level - data.z 
    return data

def get_df(path):
    df = xr.open_dataset(path)
    df['z'] = df['z'] * -1.
    return df.where(df.status > -1, drop = True)
