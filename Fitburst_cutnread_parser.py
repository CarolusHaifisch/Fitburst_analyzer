# -*- coding: utf-8 -*-
"""
Created on Thu May  9 14:34:19 2024

@author: ktsan
"""
import glob
import os
import Fitburst_singlecut_mod as fbsc
import argparse
import numpy as np
import json
from multiprocessing import Process, Pool 
# Load files for analysis (Read in names of candidates)
#files = glob.glob(r'\\wsl.localhost\Ubuntu\home\ktsang45\*.fil')

#for file in files:
    
"""Use Argparse to enable command line inputs"""
parser = argparse.ArgumentParser()
parser.add_argument(
    "pulse_folder", 
    action="store", 
    type=str,
    help="Folder containing all the candidate pulses to be analyzed")
parser.add_argument(
    'fils_path', 
    action='store', 
    type=str,
    help='Path to all .fil files to be analyzed')
parser.add_argument(
    'npz_path', 
    action='store', 
    type=str,
    help='Path to all .npz files to be analyzed')

args = parser.parse_args()
pulse_folder = args.pulse_folder
fils_path = args.fils_path
npz_path = args.npz_path

"""Decide on where to cut the blocks here, then pass the cutting parameters
as arguments into Fitburst_singlecut_mod.py to cut each file and generate
an .npz file for each. """
    
#files = os.listdir(r'\\wsl.localhost\Ubuntu\home\ktsang45\positive_bursts_1')
files = os.listdir(pulse_folder)
filtime = []
fildm = []

def splitfil_name(f):
    filparts = file.split('_')
    filtime.append(filparts[4])
    fildm.append(filparts[6])

if __name__ == '__main__':
    pool = multiprocessing.Pool()
    for file in files:
        proc = Process(target=splitfil_name, args = (file,))
        procs.append(proc)
        proc.start()            
    for proc in procs:
        proc.join()
    
filmjd = str(int(float(files[0].split('_')[2])))

#filfiles = glob.glob(r'\\wsl.localhost\Ubuntu\home\ktsang45\*.fil')
filfiles = glob.glob(fils_path + r'/*.fil')
fils_to_run = []
for file in filfiles:
    if filmjd in file:
        fils_to_run.append(file)
print(fils_to_run)

toa_list = []

#for file_run in fils_to_run:
tstart_list = []
procs=[]
def singlecut_append(ftr, fstart, fdm, ft):
    tstart_list.append(fbsc.singlecut(ftr, fstart, fdm, ft))
if __name__ == '__main__':
    for i in range(len(files)):
        proc= Process(target=singlecut_append,
                      args=(fils_to_run[0], float(filtime[i])-0.5, float(fildm[i]), filtime[i],))
        procs.append(proc)
    for proc in procs:
        proc.join()
    tstart_list = np.array(tstart_list)
procs = []

#npz_files = os.listdir(r'C:\Users\ktsan\Desktop\Research\NPZ_files')
npz_files = [i for i in os.listdir(npz_path) if '.npz' in i]
print('test')
def fitpipe(i):
    os.system('python fitburst_pipeline.py '  +' --outfile '+ npz_files[i] )
"""Multiprocessing code"""
if __name__ == '__main__':
    for i in range(len(npz_files)):
        filparts = npz_files[i].split('_')
        filtime.append(filparts[3])
        proc = Process(target=fitpipe, args=(i,))
        procs.append(proc)
        proc.start()
        
    for proc in procs:
        proc.join()
    
""" Some code for reading the TOA from the results json file"""
results_files = [i for i in os.listdir(npz_path) if '.json' in i]
results_toa = []
ref_freqs = []
mjd_errors = []
procs = []
def make_tim(i):
    with open(results_files[i], 'r') as f:
        data = json.load(f)
        results_toa.append((data['model_parameters']['arrival_time'][0]-0.5)/86400)
        ref_freqs.append(800)
        if (isinstance(data['fit_statistics']['bestfit_uncertainties']['arrival_time'][0], float) and 
        (not np.isnan(data['fit_statistics']['bestfit_uncertainties']['arrival_time'][0]))) :
            mjd_errors.append(data['fit_statistics']['bestfit_uncertainties']['arrival_time'][0])
        else:
            mjd_errors.append(1e-6)
if __name__ == '__main__':
    for i in range(len(results_files)):
        proc = Process(target=make_tim, args=(i,))
        procs.append(proc)
        proc.start()
    for proc in procs:
        proc.join()
print("Results_TOA", results_toa)
filtime = [float(i) for i in filtime]
filtime = np.array(filtime)/86400
print(len(npz_files))
    
"""Some code here for calling  fitburst_pipeline.py on the .npz files and 
    iterate over them."""

toa_list.append(tstart_list+filtime+results_toa)
print("TOA_list", toa_list)
print(len(toa_list))


""" Save data to .tim file"""
res_file = open('pulsar_timing_results.tim', 'w')
txt_list = []
for i in range(len(npz_files)):
    txt_line = ([j for j in fils_to_run[0].split("/") if '.fil' in j][0].removesuffix('.fil')
                + ' ' + str(ref_freqs[i]) + ' ' + str(toa_list[0][i]) + ' ' 
                + str(mjd_errors[i]) + ' y  \n')
    txt_list.append(txt_line)
res_file.writelines(txt_list)
res_file.close()
    