#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 09:21:10 2023

@author: jeromeguterl
"""

from parallel_job_launcher import *
import os
import shutil

# -----------------------------------------------------------------------------
# -- set bout++ directory containing bout++ executable
boot_exec_path = "/home/guterlj/boundary/hermes/hermes-3-petsc/build/"
# -- set name of bout++ executable
boot_exec = "hermes-3" 

# -- define simulation directory where simulations are stored 
sim_directory = "/home/guterlj/boundary/hermes/hermes_1D_try"
if not os.path.isdir(sim_directory):
    os.makedirs(sim_directory)


# --setup launcher
launcher = BoutParallelJobLauncher(sim_directory, boot_exec_path, boot_exec)
#-----------------------------------------------------------------------------
# -- original bout config file
bout_configfile = '/home/guterlj/boundary/hermes/hermes-3-petsc/build/examples/1D-hydrogen/BOUT.inp'

# -- define parameters to be parsed
params = {}
params["Pd+.powerflux"] = [1.5e7, 2.5e7, 3.5e7]

# -- header command for the batch script
header_commands = ["module purge",
                   "module load env/gcc8.x"]
# set simulation basename
sim_basename = "test_hydrogen1"
# -- setup simulations
launcher.setup_array_runs(params, 
                          bout_configfile,
                          casename=sim_basename, 
                          header_commands=header_commands)
# -----------------------------------------------------------------------------
# -- configure slurm tasks
slurm_options = {}
slurm_options['p'] = 'ga-ird'
slurm_options['J'] = ''
slurm_options['t'] = '02-00:00:00'
slurm_options['cpus-per-task'] = '10'
slurm_options['o'] = '%j.o'
slurm_options['e'] = '%j.e'
# -- submit jobs
launcher.sbatch(slurm_options)
# -----------------------------------------------------------------------------