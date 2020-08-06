![Build status][image-1]
![CodeBeat][image-2]
![CodeCov][image-3]

# Simulating particles and sedimentation in Glomma river

**Langragian particle tracking framework**
Repository for developing sediment module for OpenDrift for modelling flow of particles in Glomma. 

Code for animating particles and plotting trajectories have been added. Any plot or animation should be initialized using the `config_plot.py`
file and the main script file `create_maps_and_animations.py`. 

**Plotting**
- `create_maps_and_animations.py` - main plot script
- `config_plot.py` - configure and setup common plot properties  
- `animate_catter.py` - class for animating particles
- `particle_tracks.py` - class for plotting the particle trajectories
- `plot_particles_at_depth.py`- plots time versus depth for three different densities / density ranges of clay

**unittests**
A number of simple unittests are used to ensure that the methods of the toolbox behaves as they should once changes have been pushed 
to Github. The tests are all unittests but we use `nose2`to run the tests and to collect coverage information.
 
 ```sh
nose2 --with-coverage
```


*16.07.2020* - updated unit tests to include tests for generating diameter, densities, and calculating terminal velocity for various buoyancies.

[image-1]:	https://badge.buildkite.com/9fe63ac4afc901fb503d10d67c26175d7071137729c00d1b17.svg
[image-2]:	https://codebeat.co/badges/8913543f-2a74-4c67-868f-d42f917338c6
[image-3]:	https://codecov.io/gh/trondkr/Glomma_particles/branch/master/graph/badge.svg