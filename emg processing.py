# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 16:16:58 2023

@author: ncoker
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import filtfilt,butter

#Sampling rate: 1000



#%% Data import
def file_import(filename):
    data = pd.read_csv(base_path,sep = '\t',usecols=[1,2,3,4,5,6],names=['time',
                                                                         'RF',
                                                                         'VM',
                                                                         'TA',
                                                                         'GM',
                                                                         'BF'],skiprows=10, header=0)
    return data

#%% Data preprocessing
def bandpass_filter(data,sample_rate=1000,lowpass=25,highpass=450, order=4):
    nyquist = sample_rate * 0.5 # Defines the nyquist frequency
    low_cut = lowpass / nyquist # Expresses cutoff relative to Nyquist frequency
    high_cut = highpass / nyquist
    b,a = butter(order,[low_cut,high_cut],'bandpass',analog=False) # Generate Butterworth coefficients
    filtered_data = np.empty((data.shape[0],data.shape[1]))
    filtered_data[:,0]= data.iloc[:,0]
    for i in range(1,5):
        filtered = filtfilt(b,a,data.iloc[:,i])
        filtered_data[:,i] = filtered
    filtered_data = pd.DataFrame(filtered_data,columns=data.columns)
    return filtered_data

def smooth_rectify(data,sample_rate = 1000,window=0.02):
    window_samples = int(sample_rate * window)
    smoothed = np.empty((data.shape[0] - (window_samples - 1),data.shape[1]))
    smoothed[:,0] = data.iloc[0:len(data) - (window_samples - 1),0]
    filtered_data = bandpass_filter(data)
    def emg_rms(filtered_data,window_samples):
        filtered_squared = np.power(filtered_data,2)
        window_tmp = np.ones(int(window_samples)) / float(window_samples)
        return np.sqrt(np.convolve(filtered_squared,window_tmp,'valid'))
    for i in range(1,5):
        smoothed[:,i] = emg_rms(filtered_data.iloc[:,i],window_samples)
    smoothed = pd.DataFrame(smoothed,columns = data.columns)
    return smoothed
        

#%% Data visualization       
def plot_emg_data(data,smoothed_data):
    fig,ax = plt.subplots(5,2)
    fig.suptitle('Raw EMG on Left, RMS on Right')
    for i in range(5):
        ax[i,0].plot(data['time'],data.iloc[:,(i+1)],label='Raw')
        ax[i,1].plot(smoothed_data['time'],smoothed_data.iloc[:,(i+1)],label='RMS')
        ax[i,0].set_title(data.columns[(i+1)])
        ax[i,1].set_title(data.columns[(i+1)])