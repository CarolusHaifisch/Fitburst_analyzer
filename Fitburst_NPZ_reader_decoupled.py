# -*- coding: utf-8 -*-
"""
Created on Wed May 22 12:37:22 2024

@author: Karl Tsang
"""
import os
import argparse

# Use Argparse to enable command line inputs
parser = argparse.ArgumentParser()
parser.add_argument(
    'index', 
    action='store', 
    type=int,
    help='Index')
parser.add_argument(
    'npz_path',
    action='store', 
    type=str,
    help='Path to all .npz files to be analyzed')

args = parser.parse_args()
ind = args.index
npz_path = args.npz_path
filtime = []
tstart_list = []
npz_files = [i for i in os.listdir(npz_path) if '.npz' in i]
filparts = npz_files[ind].split('_')
filtime.append(filparts[3])
tstart_list.append(filparts[4])
# System call to run the fitburst pipeline fitting on each of the .npz files
os.system('python '+ npz_path + 'fitburst_pipeline.py '  +' --outfile '+ npz_path + npz_files[ind] + ' ' + npz_path )
