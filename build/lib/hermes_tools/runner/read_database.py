from scripts.materials import *

import numpy as np
import os
log = np.load("/home/guterlj/boundary/RustBCA/FusionMaterialErosion.jl/database_v0/log.npy", allow_pickle=True).tolist()
dic ={}
dic['element'] = {"tungsten":"W", "helium":"He", "deuterium":"D", "boron":"B", "neon":"Ne",
             "krypton":"Kr", "silicon":"Si", "argon":"Ar", "oxygen":"O", "copper":"Cu", "xenon ":"Xe"}
dic['Y'] = {}
database_path = 'database_v0'
for p in log['sims_param_array']:
    target = p[0]
    projectile = p[1]
    print(target)

    fp = os.path.join(database_path,"Y_R_{}_{}_v0.npy".format(dic['element'][target], dic['element'][projectile]))
    if target not in dic['Y'].keys():
        dic['Y'][target] = {}
    if projectile not in dic['Y'][target].keys():
        dic['Y'][target][projectile] = {}
    print("reading {} ... : ".format(fp))
    try:
        dic['Y'][target][projectile] = np.load(fp, allow_pickle=True).tolist()
        print("success")
    except:
        print("fail")

np.save(os.path.join(database_path,"processed_database.npy"), dic)







