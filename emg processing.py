#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  2 16:07:16 2023

@author: sarah
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 15:24:57 2023

@author: sarah
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 16:16:58 2023

@author: ncoker
"""

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import filtfilt,butter

#Sampling rate: 1000

#TODO: Implement multi-file import
#TODO: Implement batch file processing
#TODO: Further testing on multiple files
#%% Data importing
def import_list(base_path,folder): # Function for generating list of files to be analyzed
    paths = [path for path in Path(base_path+folder).resolve().glob('**/*.emt')] # Generates a list of all files in a folder containing the .emt file extension
    return paths # returns list of file paths to use for file importing

def file_import(filename): # Function for creating a formatted dataframe from .emt file obtained from path list
    # skips first 10 rows to remove header, reformats column names, and returns dataframe    
    data = pd.read_csv(filename,sep = '\t',usecols=[1,2,3,4,5,6],names=['time',
                                                                         'RF',
                                                                         'VM',
                                                                         'TA',
                                                                         'GM',
                                                                         'BF'],skiprows=10, header=0)
    return data

#%% Data preprocessing
def bandpass_filter(data,sample_rate=1000,lowpass=20,highpass=450, order=4):
    # Defines a filtering function that will be called within smooth_rectify. Don't use this function on its own. 
    nyquist = sample_rate * 0.5 # Defines the nyquist frequency
    low_cut = lowpass / nyquist # Expresses lowpass cutoff relative to Nyquist frequency
    high_cut = highpass / nyquist # Expresses highpass cutoff relative to Nyquist frequency
    b,a = butter(order,[low_cut,high_cut],'bandpass',analog=False) # Generate Butterworth coefficients
    filtered_data = np.empty((data.shape[0],data.shape[1])) #Generates empty numpy array to store filtered data
    filtered_data[:,0]= data.iloc[:,0] # Sets first column of filtered_data equal to time values from dataframe
    for i in range(1,6):
        filtered = filtfilt(b,a,data.iloc[:,i]) # Apply Butterworth filter to data
        filtered_data[:,i] = filtered # Add filtered data to numpy array
    filtered_data = pd.DataFrame(filtered_data,columns=data.columns) #Convert numpy array to dataframe and return
    return filtered_data

def smooth_rectify(data,sample_rate = 1000,window=0.02):
    window_samples = int(sample_rate * window) #calculates the number of samples in RMS moving window
    smoothed = np.empty((data.shape[0] - (window_samples - 1),data.shape[1])) #Creates empty numpy array to store data
    smoothed[:,0] = data.iloc[0:len(data) - (window_samples - 1),0]
    filtered_data = bandpass_filter(data) #Apply bandpass_filter function to data
    rectified = abs(filtered_data) #takes absolute value of complete filtered signal for rectification
    def emg_rms(rectified,window_samples): #Defines function for calculating moving RMS
        filtered_squared = np.power(rectified,2) #Square rectified signal
        window_tmp = np.ones(int(window_samples)) / float(window_samples)
        return np.sqrt(np.convolve(filtered_squared,window_tmp,'valid')) #Return moving RMS of signal
    for i in range(1,6):
        smoothed[:,i] = emg_rms(rectified.iloc[:,i],window_samples) #Apply smooth_rectify function over all columns of EMG
    smoothed = pd.DataFrame(smoothed,columns = data.columns) #Convert numpy array to dataframe and return 
    return smoothed

#%% Peak RMS Calculation
def rms_peak(smoothed, smoothed2):
    '''
    Accepts two dataframes of processed EMG data, finds max of all columns in each dataframe, 
    and calculates averaage of each trial across all muscles. Returns a dataframe with peak rms of each trial and average RMS of each trial.

    Parameters
    ----------
    smoothed : Dataframe
        Five channels of EMG RMS data with time values
    smoothed2 : Dataframe
        ive channels of EMG RMS data with time values

    Returns
    -------
    rms_peak : Dataframe
        Five rows by 3 columns of RMS max of each muscle by trial and average by muscle across trials.

    '''
    rms_peak = np.zeros((5,3)) # Create numpy array of zeros to store data
    for i in range(1,6):
        peak_rms = smoothed.iloc[:,i].max() #Find max RMS, which should occur at peak_index
        peak_rms2 = smoothed2.iloc[:,i].max()
        rms_peak[i-1,0:3] = [peak_rms,peak_rms2,(peak_rms+peak_rms2)/2] #Store values to numpy array
    rms_peak = pd.DataFrame(rms_peak,index = smoothed.columns[1:7],columns=['rms_trial1','rms_trial2','mean_rms']) # convert numpy array to dataframe
    return rms_peak


#%% Data visualization       
def plot_emg_data(data,smoothed_data): # Create plots of all EMG channels with Raw EMG on left, RMS on right
    fig,ax = plt.subplots(5,2)
    fig.suptitle('Raw EMG on Left, RMS on Right')
    for i in range(5):
        ax[i,0].plot(data['time'],data.iloc[:,(i+1)],label='Raw')
        ax[i,1].plot(smoothed_data['time'],smoothed_data.iloc[:,(i+1)],label='RMS')
        ax[i,0].set_title(data.columns[(i+1)])
        ax[i,1].set_title(data.columns[(i+1)])
        