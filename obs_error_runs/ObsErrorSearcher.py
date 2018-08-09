'''
Code to automatically find an observation error variance that approaches the intended result
The purpose of this script is to find an observation error variance for wind and concentration
in the DART simple_advection model
such that the RMSE produced is the most similar to the target RMSE
'''

#The original error variances are
#4.0099999999999998 for wind
#100001000.20000000 for concentration

#Imports
import f90nml #For parsing namelist files
import os #For messing with file system
import subprocess #For running the perfect_model_obs and filter code
import pexpect #For editing the obs error variance during the run
import math #Useful for doing indices
import sys #Useful for outputting the program results

#-----------------------------------------------------------------------------------
# FUNCTIONS
#-----------------------------------------------------------------------------------

#Get the RMSE with current run parameters
def getRMSE():
    #Run the perfect_model_obs code
    subprocess.call("./perfect_model_obs")
    #Run the filter to produce the results
    subprocess.call("./filter")
    #Format the results nicely into RMSE and spread
    subprocess.call(["rm", "rms_spread_case"])
    #For this to work the matlab scripts associated with this experiment need to be in the matlab path
    p = subprocess.Popen(["matlab", "-nodesktop", "-nosplash", "-nodisplay"], stdin=subprocess.PIPE)
    p.communicate("prior_post")
    #Get the results and convert them into an array
    #This analysis is specific to the experiment
    with open("rms_spread_case", "r") as resultsfile:
        results = resultsfile.read().replace(" ", "").split(",")[:-1]
    resultRMSE = results[measuredVariable]
    print(resultRMSE)

def runObservations(errorVariances):
    child = pexpect.spawn("./create_obs_sequence", logfile=sys.stdout)
    #subprocess.call("ls")
    child.expect("upper bound")
    child.sendline("20")
    child.expect("copies")
    child.sendline("0")
    child.expect("quality control")
    child.sendline("0")
    for i in range(20):
        child.expect("no more obs")
        child.sendline("0")
        child.expect("CONCENTRATION")
        child.sendline(str(int(2 + math.floor(i / 10))))
        child.expect("location")
        child.sendline(str(((i / 10) % 0.1 + 0.05)))
        child.expect("time")
        child.sendline("0")
        child.sendline("0")
        child.expect("variance")
        child.sendline(str(errorVariances[int(math.floor(i / 10))]))
    child.expect("filename")
    child.sendline('')
    child = pexpect.spawn("./create_fixed_network_seq", logfile=sys.stdout)
    child.expect("filename")
    child.sendline("")
    child.expect("enter 2")
    child.sendline("1")
    child.expect("times")
    child.sendline("5500")
    child.expect("(as integers)")
    child.sendline("0")
    child.sendline("0")
    child.expect("(in days and seconds)")
    child.sendline("0")
    child.sendline("3600")
    child.expect("output file")
    child.sendline("")
    child.expect("Finished")
    print("Done sending!")



#-----------------------------------------------------------------------------------
# RUN PARAMETERS
#-----------------------------------------------------------------------------------

#Target result
#Concentration analysis
targetRMSE = 3068.281481
measuredVariable = 4
#Concentration preassim
#targetRMSE = TODO
#measuredVariable = 0
#Wind analysis
#targetRMSE = 4.376807
#measuredVariable = 6
#Wind preassim
#targetRMSE = TODO
#measuredVariable = 2

#The fraction of the target result that can be error
tolerance = 0.05

#Set the path to the work directory of the model that is being used
workPath = "../../../DART/concentration_observations/models/simple_advection/work/"
returnPath = "../../../../../Programming/Science-Scripts/obs_error_runs"
os.chdir(workPath)
#Set the name of the file to write data to
#It will be opened every run to make sure that the data is not lost if the code errors
datafile = "data.csv"

#Set the target namelist
namelist = f90nml.read("input.nml")
#Set the run parameters
namelist["filter_nml"]["ens_size"] = 80
namelist["assim_tools_nml"]["filter_kind"] = 8
namelist["filter_nml"]["inf_initial"][0] = 1
namelist["assim_tools_nml"]["cutoff"] = 1000000
namelist["obs_kind_nml"]["assimilate_these_obs_types"] = ["TRACER_CONCENTRATION", "VELOCITY"]

#Write any changes to the name list into the actual file
#TODO: Use patches here instead
#This is currently done by removing the file and creating a new one,
#which could damage the namelist - use carefully
#TODO: find a safer way to write namelists
subprocess.call(["rm", "input.nml"])
namelist.write("input.nml")
subprocess.call(["rm", ".input.nml.swp"])



currentRMSE = 0
currentVariance = 0
bigVariance = 100001000.20000 #An upper bound on variance searching
constVariance = 4.0099999999999998 #Keeping the variance for the other variable constant
smallVariance = 10 # A lower bound on variance searching
bigRMSE = None # The RMSE of the upper bound on variance searching
smallRMSE = None # The RMSE for the lower bound of variance searching

print("Looking for RMSE of ", targetRMSE)
os.chdir(returnPath)
with open(datafile, "a") as data:
    data.write("Variance , RMSE\n")
os.chdir(workPath)

#TUNING
runObservations(tuple([constVariance, bigVariance]))
subprocess.call("./perfect_model_obs")
#Run the filter to produce the results
subprocess.call("./filter")
#Format the results nicely into RMSE and spread
subprocess.call(["rm", "rms_spread_case"])
#For this to work the matlab scripts associated with this experiment need to be in the matlab path
p = subprocess.Popen(["matlab", "-nodesktop", "-nosplash", "-nodisplay"], stdin=subprocess.PIPE)
p.communicate("prior_post")
#Get the results and convert them into an array
#This analysis is specific to the experiment
with open("rms_spread_case", "r") as resultsfile:
    results = resultsfile.read().replace(" ", "").split(",")[:-1]
bigRMSE = float(results[measuredVariable])

os.chdir(returnPath)
with open(datafile, "a") as data:
    data.write(str(bigVariance) + "," + str(bigRMSE) + "\n")
os.chdir(workPath)

runObservations(tuple([constVariance, smallVariance]))
subprocess.call("./perfect_model_obs")
#Run the filter to produce the results
subprocess.call("./filter")
#Format the results nicely into RMSE and spread
subprocess.call(["rm", "rms_spread_case"])
#For this to work the matlab scripts associated with this experiment need to be in the matlab path
p = subprocess.Popen(["matlab", "-nodesktop", "-nosplash", "-nodisplay"], stdin=subprocess.PIPE)
p.communicate("prior_post")
#Get the results and convert them into an array
#This analysis is specific to the experiment
with open("rms_spread_case", "r") as resultsfile:
    results = resultsfile.read().replace(" ", "").split(",")[:-1]
smallRMSE = float(results[measuredVariable])

os.chdir(returnPath)
with open(datafile, "a") as data:
    data.write(str(smallVariance) + "," + str(smallRMSE) + "\n")
os.chdir(workPath)

currentVariance = (bigVariance + smallVariance) / 2
currentRMSE = smallRMSE

print("Done Tuning")

#Begin searching!
print(currentRMSE - targetRMSE)
print(targetRMSE * tolerance)
while abs(currentRMSE - targetRMSE) > targetRMSE * tolerance:
    print("Testing variance ", currentVariance)
    runObservations(tuple([constVariance, currentVariance]))
    subprocess.call("./perfect_model_obs")
    #Run the filter to produce the results
    subprocess.call("./filter")
    #Format the results nicely into RMSE and spread
    subprocess.call(["rm", "rms_spread_case"])
    #For this to work the matlab scripts associated with this experiment need to be in the matlab path
    p = subprocess.Popen(["matlab", "-nodesktop", "-nosplash", "-nodisplay"], stdin=subprocess.PIPE)
    p.communicate("prior_post")
    #Get the results and convert them into an array
    #This analysis is specific to the experiment
    with open("rms_spread_case", "r") as resultsfile:
        results = resultsfile.read().replace(" ", "").split(",")[:-1]
    currentRMSE = float(results[measuredVariable])
    print("Reached ", currentRMSE, " with variance ", currentVariance)

    os.chdir(returnPath)
    with open(datafile, "a") as data:
        data.write(str(currentVariance) + "," + str(currentRMSE) + "\n")
    os.chdir(workPath)

    if currentRMSE <= targetRMSE:
        smallVariance = currentVariance
    elif currentRMSE > targetRMSE:
        bigVariance = currentVariance
    currentVariance = (bigVariance + smallVariance) / 2
'''
for variance in range(10, 100000010, 10000000):
    print("Testing variance ", variance)
    runObservations(tuple([constVariance, variance]))
    subprocess.call("./perfect_model_obs")
    #Run the filter to produce the results
    subprocess.call("./filter")
    #Format the results nicely into RMSE and spread
    subprocess.call(["rm", "rms_spread_case"])
    #For this to work the matlab scripts associated with this experiment need to be in the matlab path
    p = subprocess.Popen(["matlab", "-nodesktop", "-nosplash", "-nodisplay"], stdin=subprocess.PIPE)
    p.communicate("prior_post")
    #Get the results and convert them into an array
    #This analysis is specific to the experiment
    with open("rms_spread_case", "r") as resultsfile:
        results = resultsfile.read().replace(" ", "").split(",")[:-1]
    currentRMSE = float(results[measuredVariable])
    print("Reached ", currentRMSE, " with variance ", variance)
    os.chdir(returnPath)
    with open(datafile, "a") as data:
        data.write(str(variance) + "," + str(currentRMSE) + "\n")
    os.chdir(workPath)
'''
print("Finally, reached ", currentRMSE, " with variance ", currentVariance)

    
