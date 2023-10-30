#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 09:21:10 2023

@author: jeromeguterl
"""

from hermes_tools.runner import *  
import os

# -----------------------------------------------------------------------------
# -- set bout++ directory containing bout++ executable
boot_exec_path = "/home/guterlj/boundary/hermes/hermes-3-petsc/build/"
# -- set name of bout++ executable
boot_exec = "hermes-3" 

# -- define simulation directory where simulations are stored 
sim_directory = "/home/guterlj/boundary/hermes/simulations/1D-hydrogen-full-recycling-test-np1"

# --setup launcher
launcher = BoutParallelJobLauncher(sim_directory, boot_exec_path, boot_exec)
#-----------------------------------------------------------------------------
# -- original bout config file
config_folder = '/home/guterlj/boundary/hermes/turbu-d3d/1D_simulations/input_scripts/'
bout_configfile = os.path.join(config_folder,'1D-hydrogen_full_recycling.inp')

# -- define parameters to be parsed
params = {}
params["Pd+.powerflux"] = [1.5e7, 2.5e7, 3.5e7]

# -- header command for the batch script
header_commands = ["module purge",
                   "module load env/gcc8.x"]
# -- setup simulations
launcher.setup_array_runs(params, 
                          bout_configfile,
                          header_commands=header_commands)
# -----------------------------------------------------------------------------
# -- configure slurm tasks
slurm_options = {}
slurm_options['p'] = 'preemptable'
slurm_options['J'] = ''
slurm_options['t'] = '02-00:00:00'
slurm_options['ntasks'] = '1'
slurm_options['o'] = '%j.o'
slurm_options['e'] = '%j.e'
# -- submit jobs
launcher.sbatch(slurm_options)
# -----------------------------------------------------------------------------