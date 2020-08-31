# coding=utf-8

import glob
from timeit import default_timer as timer
from typing import List

import dask.dataframe as dd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from haversine import haversine
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator

# from fast_histogram import histogram2d
import bathymetry
import common_tools_drift as ct
import config_plot
import config_sedimentdrift
from circle_of_distance import Circle_of_distance


class SedimentDistribution():

    def __init__(self):
        self.config = config_plot.ConfigPlot()
        self.config_sedimentdrift = config_sedimentdrift.MartiniConf()
        self.bath = bathymetry.Bathymetry(self.config)
        self.bath.add_bathymetry_from_etopo1()
        self.dx = None;
        self.dy = None;
        self.lon_bins = None;
        self.lat_bins = None

    def get_start(self, d, n):
        # find index of the release event,
        # first non masked element
        arr = np.ma.masked_invalid(d.dif_depth[n].values)
        if arr.count() == 0:
            return None
        return np.ma.flatnotmasked_edges(arr)[0]

    def get_active_passive(self, status):
        return ["active", "passive"][status]

    def filter_data(self, df, filter_options: List):
        np.warnings.filterwarnings('ignore')

        df = df[df.status == (filter_options["status"])]

        if "density_max" and "density_min" in filter_options.keys() and not None:
            df = df[(df.density >= float(filter_options["density_min"]))
                    & (df.density <= float(filter_options["density_max"]))
                    & (df.status == int(filter_options["status"]))]

        if "selected_month" in filter_options.keys() and filter_options["selected_month"] is not None:
            df = df[df.time.dt.month == int(filter_options["selected_month"])]

        if "selected_day" in filter_options.keys() and not None:
            df = df[df.time.dt.day == int(filter_options["selected_day"])]

        return df

    def return_ds(self, data):
        return data

    def get_indexes_of_last_valid_position(self, ds, var_name="density"):
        # Assuming coordinates [time, trajectory]
        masked_data = np.ma.masked_invalid(ds[var_name].values)
        firstlast = np.ma.notmasked_edges(masked_data, axis=0)

        return firstlast[1][0]

    def extract_filtered_data(self, file_list: List, filter_options: List):

        print("[Probability] Start filtering dataframe using dask")
        start = timer()

        # Get the data and group by trajectory
        df = xr.open_mfdataset(file_list, concat_dim='trajectory', combine='nested').to_dataframe()
        # Convert from multi-index (date - trajectory) to single index (date) to use Dask
        df = df.reset_index(level="time")

        # Convert to Dask dataframe with chunks
        ddf = dd.from_pandas(df, 10)

        # This one returns a Pandas dataframe
        ddf = self.filter_data(ddf, filter_options).compute()

        ddf = ddf.set_index(['time', ddf.index])
        ds = ddf.groupby("trajectory").apply(self.return_ds).to_xarray()

        end = timer()
        print("[Probability] Finished filtering dataframe in {} seconds ".format(end - start))

        indexes = self.get_indexes_of_last_valid_position(ds)

        lons = np.ma.masked_invalid(ds.lon[indexes, :].values)
        lats = np.ma.masked_invalid(ds.lat[indexes, :].values)

        z = np.ma.masked_invalid(ds.z[indexes, :].values)
        time = np.ma.masked_invalid(ds.time[indexes].values)

        return np.array([np.array(xi) for xi in lats]), np.array([np.array(xi) for xi in lons]), np.array(
            [np.array(xi) for xi in z]), np.array([np.array(xi) for xi in time])

    def createBins(self):

        print('func: createBins() => Creating bins for averaging')

        dy = haversine((self.config.ymin, self.config.xmin), (self.config.ymax, self.config.xmin))
        dx = haversine((self.config.ymin, self.config.xmin), (self.config.ymin, self.config.xmax))

        print("Distance from minimum to maximim longitude binned area is %s km" % (dx))
        print("Distance from minimum to maximim latitude binned area is %s km" % (dy))

        nx = int(abs(dx / self.config.required_resolution))
        ny = int(abs(dy / self.config.required_resolution))
        #   print("nx {} ny {}".format(nx, ny))

        self.lon_bins = np.linspace(np.floor(self.config.xmin), np.ceil(self.config.xmax), nx, endpoint=True)
        self.dx = len(self.lon_bins)
        #   print("DELTA X = {}".format(self.lon_bins))

        self.lat_bins = np.linspace(np.floor(self.config.ymin), np.ceil(self.config.ymax), ny, endpoint=True)
        #    print("DELTA Y = {}".format(self.lat_bins))
        self.dy = len(self.lat_bins)

        print('=> created binned array of domain of grid cell size (%s,%s) with resolution %s' % (
            self.dx, self.dy, self.config.required_resolution))

    def get_density(self, lats, lons, nlevels):

        density, xedges, yedges = np.histogram2d(lons.flatten(), lats.flatten(),
                                                 range=[[self.config.xmin, self.config.xmax],
                                                        [self.config.ymin, self.config.ymax]],
                                                 bins=[self.dx, self.dy])

        total = np.sum(density)
        density = (density / total) * 100.

        print("Total number of points {} percentage sum {}".format(total, np.sum(density)))
        density = np.ma.masked_where(density == 0, density)
        levels = MaxNLocator(nbins=nlevels).tick_values(0.1, 2)
        levels = np.arange(0.1, 4, 0.1)
        cmap = plt.get_cmap('Spectral_r')

        norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)

        density = density.T
        Xd, Yd = np.meshgrid(xedges, yedges)

        return Xd, Yd, density

    def create_distributional_map(self, filelist, filter_options):

        lats, lons, depths, times = self.extract_filtered_data(filelist, filter_options)

        start_date = pd.to_datetime(times[0])
        end_date = pd.to_datetime(times[-1])

        output_filename = ct.create_animation_or_png_filename(start_date, end_date, "clay", "png")

        self.createBins()
       # confobj.mymap.drawparallels(confobj.lat_bins,linewidth=0.2, fmt='%g'+ 'E', fontsize=5, color='gray', labels=[True,False,False,False])
       # confobj.mymap.drawmeridians(confobj.lon_bins,linewidth=0.2, fmt='%g'+ 'E', fontsize=5, color='gray',labels=[False,False,False,True])

        nlevels = 10
        Xd, Yd, density = self.get_density(lats, lons, nlevels)

        cplot = self.config.ax.pcolormesh(Xd, Yd, density,
                                          cmap="RdYlBu_r",
                                          edgecolors='face',
                                          linewidths=0.1)
        # cs = confobj.mymap.contourf(Xd[:-1, :-1],Yd[:-1, :-1], density, cmap=confobj.cmap,levels = 50) #,edgecolors='face',linewidths=0.1) #,alpha=0.8)  #norm=norm,

        # Seed area drawn as a circle
        cs = Circle_of_distance()
        X, Y = cs.create_circle_with_radius(self.config_sedimentdrift.st_lats[0],
                                            self.config_sedimentdrift.st_lons[0],
                                            self.config_sedimentdrift.release_radius)

        self.config.ax.plot(self.config_sedimentdrift.st_lons[0],
                            self.config_sedimentdrift.st_lats[0],
                            marker='D',
                            color='r',
                            markersize=2)
        plt.colorbar(cplot, shrink=0.7)

        self.config.ax.plot(X, Y, marker="o", color='r', linewidth=2.9)
        print(X, Y)

        print("Printing figure to file {} ".format(output_filename))
        plt.savefig(output_filename, format='png', dpi=300)
        plt.show()


def main():
    infilenames = glob.glob("output/*.nc")

    filter_options = {"density_min": 0,
                      "density_max": 2000.,
                      "selected_month": None,
                      #               "selected_day": 7,
                      "status": 1}
    for infile in infilenames:
        distribution = SedimentDistribution()
        distribution.create_distributional_map([infile], filter_options)


if __name__ == "__main__":
    main()
