import xarray as xr
import numpy as np
import os

def get_pos_function_of_time(paths):
 
    df = xr.open_mfdataset(paths,concat_dim='trajectory',combine='nested')
    df = df.where(df.status > -1, drop = True)
    d = df.groupby(df.trajectory).apply(find_depth)
    
    return d

def find_depth(data):
    data['z'] = data['z'] * -1.
    # ! find first non nan at first and cut the rest 
    #data = data.where(data.z != 'nan')
    data = data.where(data.z != np.nan)
    data = data.where(data.sea_floor_depth_below_sea_level != 'nan',drop = True)
    # find differences between floor depth and particle depth for each trajectory
    data['dif_depth'] =  data.sea_floor_depth_below_sea_level - data.z 
    return data

def create_animation_or_png_filename(start_date,end_date, particle, postfix):

    start_date_str: str = '{}{}{}'.format(str(start_date.year),
                                          str(start_date.month).zfill(2),
                                          str(start_date.day).zfill(2))

    end_date_str: str = '{}{}{}'.format(str(end_date.year),
                                        str(end_date.month).zfill(2),
                                        str(end_date.day).zfill(2))

    output_filename = 'Figures/Glomma_{}_drift_{}_to_{}.{}'.format(particle, start_date_str,
                                                                   end_date_str,
                                                                   postfix)
    if not os.path.exists('Figures'): os.mkdir('Figures')
    if os.path.exists(output_filename):
        os.remove(output_filename)

    print("[common_tools_drift] Animation files will be stored as: {}".format(output_filename))

    return output_filename