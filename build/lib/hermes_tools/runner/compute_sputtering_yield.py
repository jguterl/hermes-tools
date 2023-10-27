#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  9 11:23:07 2023

@author: jeromeguterl
"""
import sys, os
import numpy as np
sys.path.insert(1, '/home/guterlj/boundary/RustBCA/rustbca')
from libRustBCA import *; from scripts.materials import *
import argparse

parser = argparse.ArgumentParser("simple_example")
parser.add_argument("--num_samples", help="An integer will be increased by 1 and printed.", type=int, default=10000, required=False)
parser.add_argument("--projectile", help="projectile", type=str, default="deuterium", required=False)
parser.add_argument("--target", help="target", type=str, default="tungsten", required=False)
parser.add_argument("--path", help="path", type=str, default="database", required=False)
args = parser.parse_args()
N_energy = 100
N_angle = 40
projectile = args.projectile
target= args.target
exec("p = {}".format(projectile))
exec("t = {}".format(target))
energy = np.logspace(0,4,N_energy)
angle = np.linspace(0.01,89,N_angle)
num_samples = args.num_samples
data = {}
data['target'] = t
data['projectile'] = p
data['num_samples'] = num_samples
Y = np.zeros((N_energy,N_angle))
R_p = np.zeros((N_energy,N_angle))
R_E = np.zeros((N_energy,N_angle))
data['R_E'] = R_E
data['R_p'] = R_p
data['Y'] = Y
for i in range(N_energy):
    for j in range(N_angle):
        
        angle_ = angle[j]
        energy_ = energy[i]
        print("{} -> {} : energy={:2.2} [{}]/ angle = {:2.2} [{}]".format(p["symbol"],t["symbol"],energy_,i,angle_,j))
        Y[i,j] = sputtering_yield(p, t, energy_, angle_, num_samples)
        R_p[i,j], R_E[i,j] = reflection_coefficient(p, t, energy_, angle_, num_samples)
np.save(os.path.abspath(args.path+"/Y_R_{}_{}_v0.npy".format(t["symbol"],p["symbol"])),data)

