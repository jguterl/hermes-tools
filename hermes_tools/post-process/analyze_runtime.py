import os, re
directory = '/home/guterlj/boundary/hermes/simulations/1D-hydrogen-full-recycling-test-np1'
outlog_fp  = os.path.join(directory,'runs/run_1/out.log') 

with open(outlog_fp) as f:
    lines = [line for line in f]

for i,line in enumerate(lines):
    if 'Run time :' in line:
        break 


