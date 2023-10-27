#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 09:14:45 2023

@author: jeromeguterl
"""

import itertools
import numpy as np
import os
import shutil
from slurm_support import *
import subprocess
import copy
from bout_parser_utils import *

def chmodx_directory(directory):
    command = 'chmod -R u+x {}'.format(directory)
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    print(output, error)


def tot_sim(params, tridyn_params={}):
    return np.prod([np.array(len(v)) for v in itertools.chain(params.values(), tridyn_params.values())])


def gnu_parallel_command(runner_exec_file, runner_input, njob):
    commands = ['module load parallel']
    commands += ['parallel -j {} {} {{}} < {}'.format(
        njob, runner_exec_file, runner_input)]
    return commands


def dump_log(filename, dic):
    np.save(filename, dic)


class BoutParallelJobLauncher():
    def __init__(self, directory, bout_exec_directory, bout_exec):
        self.sim_setup = {}
        self.njobs = 0
        assert os.path.isdir(directory), f"Cannot find the directory {directory}"
        self.directory = os.path.abspath(directory)
        assert os.path.isdir(bout_exec_directory), f"cannot find the bout exec directory {bout_exec_directory}"
        self.bout_exec_directory = bout_exec_directory
        bout_exec = os.path.join(bout_exec_directory,bout_exec)
        assert os.path.isfile(bout_exec), f"cannot find the bout exec file {bout_exec}"
        self.bout_exec = bout_exec
        
    def setup_array_runs(self, params, boutconfig_file, options={}, casename='run', header_commands=[], sim_folder='simulations', bout_configfn = 'BOUT.inp'):

        dic = {}
        fp = os.path.abspath(boutconfig_file)
        assert os.path.isfile(fp ), f"Cannot find the bout config file {fp}"
        dic['directory'] = os.path.abspath(self.directory)
        dic['original_bout_configfile'] = fp
        # write a copy in the directory
        cf_fn = os.path.join(dic['directory'],os.path.basename(fp)+"_original")
        shutil.copyfile(dic['original_bout_configfile'], cf_fn)
        original_bout_config = parse_bout_configfile(fp)
        
        dic['params'] = params
        dic['options'] = options
        dic['sim_folder'] = sim_folder
        dic['nsim'] = np.prod([np.array(len(v)) for v in params.values()])

        sims = {}
        sim_param_array = np.empty(
            (dic['nsim'], len([k for k in params.values()])), dtype=object)

        for i, val in enumerate(itertools.product(*(v for v in params.values()))):
            print('Setup simulation # {} with :'.format(i), ';'.join(
                ['{}={}'.format(k, val) for k, val in zip(params.keys(), val)]))
            sim = {}
            val_params = val[0:len(list(params.keys()))]
            sim['original_bout_configfile'] = dic['original_bout_configfile']
            sim['params'] = dict((k, v)
                                 for k, v in zip(params.keys(), val_params))
            sim_param_array[i, :] = np.array([v for v in val], dtype=object)
            config = modify_bout_parameters(original_bout_config,sim['params'])
            
            sim['options'] = options
            sim['casename'] = '{}_{}'.format(casename, i)
            bout_dir = os.path.join(dic['directory'],dic['sim_folder'], sim['casename'])
            assert not os.path.isdir(bout_dir), f"the directory {bout_dir} already exists ... Overwrite is not permitted..."
            sim['bout_dir'] = bout_dir

            sim['bout_exec'] = self.bout_exec
            sim['bout_exec_directory'] = self.bout_exec_directory

            
            print(f"Creating bout simulation directory { bout_dir} ...")
            os.makedirs(sim['bout_dir'])


            bout_configfile = os.path.join(sim['bout_dir'],bout_configfn)
            print(f"Writing bout config file:{bout_configfile} ...")
            write_bout_configfile(bout_configfile,config)

            self.make_command_line(sim, header_commands)
            sims[i] = sim

        dic['sims_param_array'] = sim_param_array
        dic['sims'] = sims
        self.sim_setup = dic
        self.njobs = len(list(self.sim_setup['sims'].keys()))

    # @staticmethod
    # def random_sampling(pval, scale=None):
    #     if scale == 'linear' or scale is None:
    #         return (np.max(pval) - np.min(pval)) * np.random.random_sample() + np.min(pval)
    #     elif scale =='log':
    #         return np.exp((np.max(np.log(pval)) - np.min(np.log(pval))) * np.random.random_sample() + np.min(np.log(pval)))
    #     else:
    #         raise ValueError("unknon scale:{}".format(scale))

    # def setup_random_runs(self, params, inputfile, nruns=100, casename='run', params_sampling=None):
    #      if params_sampling is None:
    #         params_sampling = dict((k,'linear') for k in params.keys())
    #      print("----- Project:",self.CurrentProject)
    #      dic={}
    #      dic['inputfile'] = os.path.abspath(inputfile)
    #      dic['directory'] = os.path.abspath(self.directory)
    #      dic['params'] = params
    #      dic['nsim'] = nruns
    #      sims = {}
    #      sim_param_array = np.zeros((dic['nsim'],len([k for k in params.values()])))

    #      for i in range(nruns):
    #          sim_params = dict((k,self.random_sampling(pval,params_sampling.get(k))  ) for k,pval in params.items() )
    #          print('Setup simulation # {} with :'.format(i),';'.join(['{}={}'.format(k,val) for k,val in sim_params.items()]))
    #          sim = {}
    #          sim['inputfile'] =  dic['inputfile']
    #          sim['params'] = dict((k,v) for k,v in  sim_params.items())
    #          sim['casename'] = '{}_{}'.format(casename,i)
    #          sim_param_array[i,:] =  np.array([v for v in sim_params.values()])
    #          self.make_command_line(sim)
    #          sims[i] = sim

    #      dic['sims_param_array'] = sim_param_array
    #      dic['sims'] = sims
    #      self.sim_setup = dic
    #      self.njobs = len(list(self.sim_setup['sims'].keys()))

    @staticmethod
    def make_command_line(sim, header_commands=[]):
        #args = " ".join(['--{}={}'.format(k, v) for (k, v) in sim['params'].items()] + [
                        #'--{}={}'.format(k, v) for (k, v) in sim['options'].items()])
        args = " "
        header_commands = copy.deepcopy(header_commands)
        command = "cd {}".format(sim['bout_exec_directory'])
        header_commands.append(command)
        command = "srun --mpi=pmi2 {} -d {} {}".format(sim['bout_exec'], sim['bout_dir'],args)
        header_commands.append(command)    
        sim['command'] = "\n".join(header_commands) + "\n"

    def setup_slurm_scripts(self, slurm_options):
        self.slurm_runners = []
        for (i, sim) in self.sim_setup['sims'].items():
            self.slurmscript_directory = os.path.join(
                self.sim_setup['directory'], 'sbatch_scripts')
            try:
                os.mkdir(self.slurmscript_directory)
            except:
                pass
            script_name = '{}.sbatch'.format(sim['casename'])
            slurm_options["J"] = sim['casename']
            slurm_options["o"] = os.path.join(
                sim['bout_dir'], "out.log")
            slurm_options["e"] = os.path.join(
                sim['bout_dir'], "err.log")
            logpath = os.path.join(
                sim['bout_dir'], "log")
            sim['logpath'] = logpath
            slurm_runner = slurm_support.SlurmSbatch(sim['command']+' >> {}'.format(
                logpath), **slurm_options, script_dir=self.slurmscript_directory, script_name=script_name, pyslurm=True)
            self.slurm_runners.append(slurm_runner)
            slurm_runner.write_job_file()

    def _sbatch(self):
        # chmodx_directory(self.directory)
        for s in self.slurm_runners:
            s.submit_job()

        # job_id = 0
        self.saveas(os.path.join(
            self.sim_setup['directory'], "log.npy"), self.sim_setup)

    def sbatch(self, slurm_options):
        self.setup_slurm_scripts(slurm_options)
        self._sbatch()

    def saveas(self, filename, obj):
        filename = os.path.join(filename)
        np.save(filename, obj)
