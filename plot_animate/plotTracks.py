# coding=utf-8
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from scipy.ndimage.filters import gaussian_filter
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import utils
import animateScatter
import tracks
import xarray as xr
import config_bekkelaget as confm
import common_tools_drift as ct
import drawCircleOfDistance

def make_map(confobj):
    
    df = xr.open_mfdataset(confobj.paths, concat_dim='trajectory') 
    df = ct.get_pos_function_of_time(confobj.paths)
    print(confobj.paths)
    lats=df['lat'][:].values
    lons=df['lon'][:].values
    z=df['z'][:].values
    time=df['time'][:].values

    if confobj.plot_type=='animate_particles':
        anim = animateScatter.AnimatedScatter(lons,lats,z,time,confobj.outputPlotFilename)
        anim.saveAnim()

    if confobj.plot_type=='plot_particletracks':
        trk = tracks.Tracks(lons,lats,z,confobj)
        trk.plot_tracks(confobj)
    
     #   plt.show()

def call_make_map(confobj):
     
    confobj.paths = ct.get_paths(confobj) 
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
                confobj.plot_type='plot_particletracks'
                call_make_map(confobj) 