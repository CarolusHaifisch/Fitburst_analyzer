# -*- coding: utf-8 -*-
"""
Created on Thu May  9 14:34:19 2024

@author: ktsan
"""
import glob
import os
import argparse
import numpy as np
from sigpyproc.readers import FilReader
import matplotlib.pyplot as plt
from iqrm  import iqrm_mask
from scipy.stats import median_abs_deviation as mad

ignored_chans = ([0] + list(range(34,48)) + list(range(113,179)) +
                 list(range(185,211)) + list(range(218,255)) + list(range(554,569)) + list(range(584,597)) +
                 list(range(631,645)) + list(range(677,694)) + list(range(754,763))+list(range(788,792))+list(range(854,861))+list(range(873,876))+[887])

def singlecut(fil_name, t_start, disp_measure, fil_time, t_origin, isddp=True):
    fbfile = FilReader(fil_name)
    sub = '.fil'
    # Remove suffix from filename for naming .npz file later
    fil_short_name = [i for i in fil_name.split("/") if sub in i][0].removesuffix(sub)
    fbh = fbfile.header
    downsamp=8 
    # Define variables
    t_block = 5
    nsamps = int(t_block/fbh.tsamp)
    nsamps = nsamps-nsamps%downsamp
    #t_start = 396.3
    print(nsamps)
    start_samp = round(t_start/fbh.tsamp)
    #print(start_samp)

    fblock = fbfile.read_block(start_samp, nsamps)
    #fbd = fbfile.read_dedisp_block(round(200/fbh.tsamp), 59000, 112.5)
    #print(fblock)

    # Remove channels depending on MJD of file
    if (int(filmjd[ind])>=59091 and int(filmjd[ind])<59093):
        ignored_chans.extend(list(range(444,470)))
    elif int(filmjd[ind])>=59093:
        ignored_chans.extend(list(range(405,470)))
    elif int(filmjd[ind])>=59523:
        ignored_chans.extend(list(range(83,108)))
    ignored_chans.extend(list(range(380,520)))
    #mask these channels
    #Mask all known RFI channels
    import copy
    fbt = copy.deepcopy(fblock)
    mn = np.mean(fbt, axis = 1)
    mask = (mn == 0)
    fbt[mask,:] = np.median(fbt[~mask,:])
    mad_mask = mad(fbt, axis=1) > 0.2
    #mask[mad_mask] = True
    fbt[mask,:] = np.median(fbt[~mask,:])
    std_on = np.std(fbt, axis=1)
    iqrmmask,votes = iqrm_mask(std_on, threshold=1, ignorechans=ignored_chans)
    mask[iqrmmask] = True
    mask[ignored_chans] = True
    fbt[mask,:] = np.median(fbt[~mask,:])
    # Identify bad channels for masking and dedisperse data if needed
    #import pdb; pdb.set_trace()
    fbt = fbt.dedisperse(130)
    fbt = fbt.downsample(downsamp,8)
    fbt = fbt.normalise()

    zoom_mid_sample = t_block/2/fbh.tsamp/downsamp
    zoom_window = 1 #second
    zoom_window_samples = zoom_window/fbh.tsamp/downsamp
    fbt_zoom = fbt[:, int(zoom_mid_sample - zoom_window_samples):int(zoom_mid_sample + zoom_window_samples)]
    fbt = fbt_zoom

    # Plot data and save
    #plt.imshow(fbt, aspect='auto')
    #Saves figure to .png image
    
    plt.imshow(fbt, aspect='auto',cmap="YlGnBu")
    plt.show()
    plt.savefig(fil_short_name + '_' + str(fil_time) + '_' + str(t_origin) + '_test.png')
    data_full = fbt
    #print(fil_short_name)
    #print(r'~/NPZ_files/'+ fil_short_name + '_' + fil_time + '.npz')
    np.savez(
        (fil_short_name + '_' + str(fil_time) + '_' + str(t_origin) + ".npz"), 
        data_full=data_full, 
        metadata=metadata, 
        burst_parameters=burst_parameters,
        )
        
    return fbh.tstart
# Load files for analysis (Read in names of candidates)
#files = glob.glob(r'\\wsl.localhost\Ubuntu\home\ktsang45\*.fil')

#for file in files:
    
"""Use Argparse to enable command line inputs"""
parser = argparse.ArgumentParser()
parser.add_argument(
    'index', 
    action='store', 
    type=int,
    help='Index')
parser.add_argument(
    "pulse_path", 
    action="store", 
    type=str,
    help="Path to .csv file containing all the candidate pulses to be analyzed")
#
parser.add_argument(
    'fils_path', 
    action='store', 
    type=str,
    help='Path to all .fil files to be analyzed')


args = parser.parse_args()
ind = args.index
pulse_path = args.pulse_path
fils_path = args.fils_path

print(pulse_path)
print(fils_path)

"""Decide on where to cut the blocks here, then pass the cutting parameters
as arguments into Fitburst_singlecut_mod.py to cut each file and generate
an .npz file for each. """
    
#files = os.listdir(r'\\wsl.localhost\Ubuntu\home\ktsang45\positive_bursts_1')
datafile = pulse_path
data = np.genfromtxt(datafile, delimiter=",", dtype=str)
files = data[:,0]
#print(files)
tstart_list = []
filtime = []
fildm = []
filmjd = []

print('test1')
for file in files:
    #print(file)
    file = file[file.find('cand'):]
    filparts = file.split('_')
    #print(filparts)
    filtime.append(filparts[4])
    fildm.append(filparts[6])
    tstart_list.append(filparts[2])
    filmjd.append(str(int(float(filparts[2]))))
#filfiles = glob.glob(r'\\wsl.localhost\Ubuntu\home\ktsang45\*.fil')
filfiles = glob.glob(fils_path + r'/*.fil')
print('filtime is ' + str(filtime))
print('start time is ' + str(tstart_list))
print('test2')

fils_to_run = []
for i in range(len(files)):
   for file in filfiles:
       if filmjd[i] in file:
            fils_to_run.append(file)
print('filstorun length ' + str(len(fils_to_run)))

toa_list = []
print('test')
#for file_run in fils_to_run:
print('filstorun length ' + str(len(fils_to_run)) + 'filtime length ' + str(len(filtime)) + 'fildm length ' + str(len(fildm)) + 'tstart length ' +str(len(tstart_list)))
print('Index '+ str(ind))
singlecut(fils_to_run[ind], float(filtime[ind])-2, float(fildm[ind]), float(filtime[ind]), float(tstart_list[ind]))
