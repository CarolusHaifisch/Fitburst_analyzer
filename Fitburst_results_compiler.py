# -*- coding: utf-8 -*-
"""
Created on Mon May 27 14:58:08 2024

@author: ktsan
"""
import os
import argparse
import numpy as np
import json

"""Use Argparse to enable command line inputs"""
parser = argparse.ArgumentParser()
parser.add_argument(
    'json_path',
    action='store', 
    type=str,
    help='Path to all .json files to be analyzed')

args = parser.parse_args()
json_path = args.json_path

toa_list = []

""" Some code for reading the TOA from the results json file"""
results_files = [i for i in os.listdir(json_path) if '.json' in i]

results_toa = []
ref_freqs = []
mjd_errors = []
filtime = []
tstart_list = []
fil_names = []
print(results_files)
for i in range(len(results_files)):
    with open(json_path + results_files[i], 'r') as f:
        data = json.load(f)
        # Check if uncertainty is a float, if nan, ignore data point
        if (isinstance(data['fit_statistics']['bestfit_uncertainties']['arrival_time'][0], float) and
                (not np.isnan(data['fit_statistics']['bestfit_uncertainties']['arrival_time'][0]))) :
            fil_names.append(results_files[i].removesuffix('_'+ str(filtime[i])+'_'+str(tstart_list[i])+'.json').removeprefix('results_fitburst_'))
            results_toa.append((data['model_parameters']['arrival_time'][0]-2)/86400)
            ref_freqs.append(800)
            filtime.append(results_files[i].split('_')[-2])
            tstart_list.append(results_files[i].split('_')[-1].removesuffix('.json'))
            mjd_errors.append(data['fit_statistics']['bestfit_uncertainties']['arrival_time'][0]*1e6)
            

'''with open(results_files[ind], 'r') as f:
    data = json.load(f)
    results_toa.append((data['model_parameters']['arrival_time'][0]-0.5)/86400)
    ref_freqs.append(800)
    if (isinstance(data['fit_statistics']['bestfit_uncertainties']['arrival_time'][0], float) and 
    (not np.isnan(data['fit_statistics']['bestfit_uncertainties']['arrival_time'][0]))) :
        mjd_errors.append(data['fit_statistics']['bestfit_uncertainties']['arrival_time'][0])
    else:
        mjd_errors.append(1e-6)'''
print("Results_TOA", results_toa)
print(filtime)
filtime = [float(i) for i in filtime]
#filtime = float(filtime[ind])
filtime = np.array(filtime)/86400

    
"""Some code here for calling  fitburst_pipeline.py on the .npz files and 
    iterate over them."""
for i in range(len(tstart_list)):    
    toa_list.append(float(tstart_list[i])+float(filtime[i])+float(results_toa[i]))
print("TOA_list", toa_list)
print(len(toa_list))
print(len(results_files))


""" Save data to .tim file"""
res_file = open('pulsar_timing_results.tim', 'w')
txt_list = []
for i in range(len(toa_list)):
    txt_line = (fil_names[i]
                + ' ' + str(ref_freqs[i]) + ' ' + str(toa_list[i]) + ' ' 
                + str(mjd_errors[i]) + ' y  \n')
    txt_list.append(txt_line)
res_file.writelines(txt_list)
res_file.close()