# coding=utf-8
import animate_scatter
import common_tools_drift as ct
import particle_tracks
import pandas as pd
import glob

def make_map():
    infilenames = glob.glob("output/*.nc")
    print("Found {} files".format(len(infilenames)))

    for infile in infilenames:
        plot_type = 'plot_particletracks'
        particle="clay"

        df = ct.get_pos_function_of_time([infile])

        lats = df['lat'][:].values
        lons = df['lon'][:].values
        z = df['z'][:].values
        time = df['time'][:].values
        start_date = pd.to_datetime(time[0])
        end_date = pd.to_datetime(time[-1])

        if plot_type == 'animate_particles':
            output_filename = ct.create_animation_or_png_filename(start_date,end_date, particle, filter_options={"status":1},
                                                                  postfix="mp4")
            anim = animate_scatter.AnimatedScatter(lons, lats, z, time, output_filename)
            anim.save_animation()

        if plot_type == 'plot_particletracks':
            output_filename = ct.create_animation_or_png_filename(start_date,end_date, particle,filter_options={"status":1},
                                                                  postfix="png")
            trk = particle_tracks.Tracks(lons, lats, z, time, output_filename)
            trk.plot_tracks()


if __name__ == "__main__":
    make_map()
