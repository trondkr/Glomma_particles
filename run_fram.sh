#!/bin/bash

##########################
# ROMS SLURM MPI job #
##########################

#SBATCH --job-name=Glomma_particles

# Set number of tasks or tasks per node (max 10 nodes on devel)
#SBATCH --ntasks-per-node=1
#SBATCH --nodes=1

#SBATCH -A nn9297k

# run time (max 7 days on normal, 30 minutes on devel, 2 hrs on short)
#              d-hh:mm:ss
##SBATCH --time=1-00:00:00
##SBATCH --time=0-00:30:00
#SBATCH --time=0-23:50:00

# choose partition
#SBATCH --partition=normal
##SBATCH --qos=devel
##SBATCH --qos=short
#SBATCH --qos=devel

# memory per core and no. nodes (only specify on bigmem partition)
##SBATCH --mem-per-cpu=1000MB

# turn on all mail notification
#SBATCH --mail-user=trond.kristiansen@niva.no
#SBATCH --mail-type=ALL

# you may not place bash commands before the last SBATCH directive

# define and create a unique scratch directory
WORK_DIRECTORY=/cluster/projects/nn9297k/Glomma_particles
SCRATCH_DIRECTORY=${WORK_DIRECTORY}
SLURM_SUBMIT_DIR=${WORK_DIRECTORY}
mkdir -p ${SCRATCH_DIRECTORY}
cd ${SCRATCH_DIRECTORY}

source /home/${USER}/.bashrc
source activate opendrift

# we execute the job and time it
time mpirun python run_sedimentdrift.py

# happy end
exit 0