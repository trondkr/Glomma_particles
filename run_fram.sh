#!/bin/bash

##########################
# ROMS SLURM MPI job #
##########################

#SBATCH --job-name=Glomma_particles

# Set number of tasks or tasks per node (max 10 nodes on devel)
#SBATCH --ntasks-per-node=4
#SBATCH --nodes=4

#SBATCH -A nn9297k

# run time (max 1 hour on devel)
#              d-hh:mm:ss
#SBATCH --time=0-12:00:00

# short partition should do it
#SBATCH --partition=normal
##SBATCH --qos=devel

# memory per core and no. nodes (only specify on bigmem partition)
##SBATCH --mem-per-cpu=1000MB

# turn on all mail notification
#SBATCH --mail-user=trond.kristiansen@niva.no
#SBATCH --mail-type=ALL

# you may not place bash commands before the last SBATCH directive

# define and create a unique scratch directory
WORK_DIRECTORY=/cluster/work/users/${USER}/hunnbunn_run01
SCRATCH_DIRECTORY=${WORK_DIRECTORY}
SLURM_SUBMIT_DIR=${HOME}/hunnbunn
mkdir -p ${SCRATCH_DIRECTORY}
cd ${SCRATCH_DIRECTORY}

# we copy everything we need to the scratch directory
# ${SLURM_SUBMIT_DIR} points to the path where this script was submitted from
cp -p /cluster/projects/nn9483k/roms_input/Hunnbunn_ROMS/Grid/hunnbunn50_grd.nc ${WORK_DIRECTORY}/.
cp -p /cluster/projects/nn9483k/roms_input/Hunnbunn_ROMS/Grid/hunnbunn50_nud.nc ${WORK_DIRECTORY}/.
cp -p ${SLURM_SUBMIT_DIR}/hunnbunn50_bry_v4.nc ${WORK_DIRECTORY}/.
cp -p /cluster/projects/nn9483k/roms_input/Hunnbunn_ROMS/Clm/hunnbunn50_clm_v3.nc ${WORK_DIRECTORY}/.
cp -p ${SLURM_SUBMIT_DIR}/hunnbunn50_ini_v5.nc ${WORK_DIRECTORY}/.
cp -p /cluster/projects/nn9483k/roms_input/Hunnbunn_ROMS/Met/hunnbunn50_met.nc ${WORK_DIRECTORY}/.
# we load the required modules
module restore system
module load OpenMPI/2.1.2-iccifort-2018.1.163-GCC-6.4.0-2.28
module load iomkl/2018a
module load netCDF/4.4.1.1-iomkl-2018a-HDF5-1.8.19
module load netCDF-Fortran/4.4.4-iomkl-2018a-HDF5-1.8.19
module list

# we execute the job and time it
time mpirun ./oceanM ocean_hunnbunn.in > output_hunnbunn_run01.log

# after the job is done we copy our output back to $SLURM_SUBMIT_DIR
# cp -p ${SCRATCH_DIRECTORY}/roho800.output ${SLURM_SUBMIT_DIR}

# we delete the forcing data on work partition (not necessary)
# rm ${WORK_DIRECTORY}/FORCING/*
# rm ${WORK_DIRECTORY}/Grid/*

# we step out of the scratch directory
cd ${SLURM_SUBMIT_DIR}

# happy end
exit 0