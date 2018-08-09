# DARTAutomation
A script to run a filter on a model and return the RMSE and spread for preassim.nc and analysis.nc.
This script is designed to be easily modifiable. To run it, both matlab files should be in your matlab path and you need to have DART (https://www.image.ucar.edu/DAReS/DART/) installed.
I put prior_post.m into <DART_INSTALL>/diagnostics/matlab and PlotTotalErr.m needs to replace the one in <DART_INSTALL>/diagnostics/matlab/private.
To change the process of the experiment, change the data collection in PlotTotalErr.m (I used the simple_advection model here) and change the interpretation of the data collection in the script.
Both of the matlab files are modifications of DART files and scripts originally written by Dr. Jeff Anderson of NCAR.