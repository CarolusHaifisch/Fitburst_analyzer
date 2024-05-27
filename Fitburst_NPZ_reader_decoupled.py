# -*- coding: utf-8 -*-
"""
Created on Wed May 22 12:37:22 2024

@author: ktsan
"""
import os
import argparse
import numpy as np
import json

"""Use Argparse to enable command line inputs"""
parser = argparse.ArgumentParser()
parser.add_argument(
    'npz_path', 
    action='store', 
    type=str,
    help='Path to all .npz files to be analyzed')

args = parser.parse_args()
npz_path = args.npz_path
filtime = []
tstart_list = []
#npz_files = os.listdir(r'C:\Users\ktsan\Desktop\Research\NPZ_files')
npz_files = [i for i in os.listdir(npz_path) if '.npz' in i]
for i in range(len(npz_files)):
    filparts = npz_files[i].split('_')
    filtime.append(filparts[3])
    tstart_list.append(filparts(4))
    print(npz_files[i])

    #os.system('python fitburst_pipeline.py ' + r'\\wsl.localhost\Ubuntu\home\ktsang45\NPZ_files' + r'\\'+ file + ' --outfile')
    os.system('python fitburst_pipeline.py '  +' --outfile '+ npz_files[i] )
toa_list = []

""" Some code for reading the TOA from the results json file"""
results_files = [i for i in os.listdir(npz_path) if '.json' in i]
results_toa = []
ref_freqs = []
mjd_errors = []
for i in range(len(results_files)):
    with open(results_files[i], 'r') as f:
        data = json.load(f)
        results_toa.append((data['model_parameters']['arrival_time'][0]-0.5)/86400)
        ref_freqs.append(800)
        if (isinstance(data['fit_statistics']['bestfit_uncertainties']['arrival_time'][0], float) and 
        (not np.isnan(data['fit_statistics']['bestfit_uncertainties']['arrival_time'][0]))) :
            mjd_errors.append(data['fit_statistics']['bestfit_uncertainties']['arrival_time'][0])
        else:
            mjd_errors.append(1e-6)
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
    txt_line = (npz_files[i].removesuffix('_'+ filtime[i]+'.npz')
                + ' ' + str(ref_freqs[i]) + ' ' + str(toa_list[0][i]) + ' ' 
                + str(mjd_errors[i]) + ' y  \n')
    txt_list.append(txt_line)
res_file.writelines(txt_list)
res_file.close()
    