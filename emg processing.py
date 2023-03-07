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
def rms_peak(smoothed):
    rms_peak = np.zeros((5,3)) # Create numpy array of zeros to store data
    for i in range(1,6):
        peak_index = smoothed.iloc[:,i].idxmax() #Find index of peak RMS from column i
        peak_time = smoothed.iloc[peak_index,0] # Find time value corresponding to peak_index
        peak_rms = smoothed.iloc[:,i].max() #Find max RMS, which should occur at peak_index
        rms_peak[i-1,0:3] = [peak_index,peak_time,peak_rms] #Store values to numpy array
    rms_peak = pd.DataFrame(rms_peak,index = smoothed.columns[1:7],columns=['peak_index','peak_time','peak_rms']) # convert numpy array to dataframe
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
        
#%% Calculate average of two trials
def average_rms_calc(rms_peak1,rms_peak2):
    rms_vals = np.zeros((5,2))
    rms_vals[:,0] = rms_peak1.iloc[:,2]
    rms_vals[:,1] = rms_peak2.iloc[:,2]
    average_rms = pd.DataFrame({'rms_trial1':rms_vals[:,0],
                                'rms_trial2':rms_vals[:,1],
                                'mean_rms': rms_vals.mean(axis=1)},
                               index = rms_peak1.index)
    return average_rms
    