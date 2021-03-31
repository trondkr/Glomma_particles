import matplotlib.pyplot as plt
import bathymetry
import config_sedimentdrift
from circle_of_distance import Circle_of_distance
import config_plot


class Tracks():

    def __init__(self, lons, lats, z, time, output_filename):
        self.z = z
        self.lons = lons
        self.lats = lats
        self.time = time
        self.output_filename = output_filename
        self.config = config_plot.ConfigPlot()
        self.config_sedimentdrift = config_sedimentdrift.MartiniConf()

        bath = bathymetry.Bathymetry(self.config)
        bath.add_bathymetry_from_etopo1()

    def plot_tracks(self):

        for traj_index in range(len(self.lons[:, 0])):
            print("[Particle_tracks] Plotting trajectory {}".format(traj_index))
            x=self.lons[traj_index, (self.lons[traj_index, :] < 1e30)]
            y = self.lats[traj_index, (self.lats[traj_index, :] < 1e30)]
            z = self.z[traj_index, (self.lats[traj_index, :] < 1e30)]

            self.config.ax.plot(x,
                                y,
                                c='k',
                                alpha=0.2,
                                linewidth=0.2)
            if len(z > 0):
               # scaled_z = (z - z.min()) / z.ptp()
                colors = plt.get_cmap('PiYG')
                print("[Particle_tracks] depth variation {} to {}".format(z.min(),z.max()))
                cbar = self.config.ax.scatter(x, y, marker=None,
                                       facecolors=colors,
                                       s=2,
                                  alpha=0.8,
                                  linewidth=0.3)

        # Seed area drawn as a circle
        cs = Circle_of_distance()
        X, Y = cs.create_circle_with_radius(self.config_sedimentdrift.st_lats[0],
                                            self.config_sedimentdrift.st_lons[0],
                                            self.config_sedimentdrift.release_radius / 1000.)
        self.config.ax.plot(X, Y, marker=None, color='y', linewidth=0.9)

        self.config.ax.plot(self.config_sedimentdrift.st_lons[0],
                            self.config_sedimentdrift.st_lats[0],
                            marker='D',
                            color='r',
                            markersize=0.4)
        plt.colorbar(cbar)
        plt.savefig(self.output_filename, format='png', dpi=300)
