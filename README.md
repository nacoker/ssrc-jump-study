# ssrc-jump-study

This repository is dedicated to all offline processing files for the SSRC Jump Feedback replication. 

## Current Capabilities (v 0.1)

This script contains functions for:
1. Reading EMG data obtained from the lower extremity using BTS FREEEMG systems
2. Filtering EMG data using a 4th order, bandpass Butterworth filter with a low-pass cutoff of 25 Hz and a high-pass cutoff of 450 Hz (though inputs can be changed)
3. Calculating the RMS of the signal over a 20 ms moving window (window length can be changed)
4. plotting raw EMG and RMS side-by-side for all recorded muscles

Planned future expansions include:
1. Calculating movement onset as the first 20ms window in which all EMG RMS data points are above 10% of maximal EMG RMS
2. Incorporating synchronization with force-time curve during countermovement jump to time-sync EMG relative to jump takeoff

     
For further reading on EMG processing and interpretation, please see [The ABCs of EMG](https://www.noraxon.com/wp-content/uploads/2014/12/ABC-EMG-ISBN.pdf) by Peter Konrad and [The ISEK Guidelines for EMG Reporting Standards](https://www1.udel.edu/biology/rosewc/kaap686/notes/EMG%20analysis.pdf) by Roberto Merletti

Created by [Nick Coker](github.com/nacoker)
