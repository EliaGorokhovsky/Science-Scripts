'''
Code to automate running filters in DART
'''
#Imports
import f90nml #For parsing namelist files
import itertools #For iterating through all of the possible combinations
#from netCDF4 import Dataset #For reading the output files of the programs; this isn't used right now, but it could be
import os #For messing with file system
import subprocess #For running the perfect_model_obs and filter code

#-----------------------------------------------------------------------------------
# FUNCTIONS
#-----------------------------------------------------------------------------------

#Write any changes to the name list into the actual file
#TODO: Use patches here instead
def writeNamelist(path):
    #This is currently done by removing the file and creating a new one,
    #which could damage the namelist - use carefully
    #TODO: find a safer way to write namelists
    os.remove(path)
    namelist.write(path)
    subprocess.call(["rm", ".input.nml.swp"], cwd=workPath)

#-----------------------------------------------------------------------------------
# RUN PARAMETERS
#-----------------------------------------------------------------------------------

#Set the path to the work directory of the model that is being used
workPath = "../../../DART/concentration_observations/models/simple_advection/work/"
#Set the path to the namelist that controls the model inputs
namelistPath = workPath + "input.nml"
#Set the name of the file to write data to
#It will be opened every run to make sure that the data is not lost if the code errors
datafile = "data.csv"

#Open the model namelist
namelist = f90nml.read(namelistPath)

#The list of ensemble sizes to check
ensembleSizes = [80]

#The list of filter kinds to check
#This dictionary will store the filter names so that they make sense when written down
filterNames = {8 : "RHF"}
filterKinds = [8]

#The list of inflation standard deviations to check
inflations = [1.0, 1.02, 1.04, 1.08, 1.16, 1.32, 1.64]

#The list of possible localization halfwidths to check
localizations = [.125, .15, .175, .2, .25, .4, 1000000]

#The list of assimilated variable sets to check
assimilatedVarSets = [["TRACER_CONCENTRATION", "VELOCITY"], ["TRACER_CONCENTRATION"], ["VELOCITY"]]

#-----------------------------------------------------------------------------------
# TRIALS
#-----------------------------------------------------------------------------------
#This is optional; uncomment it to reset the observations every run
subprocess.call("./perfect_model_obs", cwd=workPath)

#Write table headers
with open(datafile, "a") as data:
    data.write("Ensemble Size, Filter Kind, Inflation, Localization Cutoff, Assimilated Variables, Diagnostic File, Concentration RMSE, Concentration Spread, Wind RMSE, Wind Spread")

#Iterate through all combinations of run parameters
for (ensembleSize, filterKind, inflation, localization, assimilatedVars) in itertools.product(ensembleSizes, filterKinds, inflations, localizations, assimilatedVarSets):
    #Set the run parameters
    namelist["filter_nml"]["ens_size"] = ensembleSize
    namelist["assim_tools_nml"]["filter_kind"] = filterKind
    namelist["filter_nml"]["inf_initial"][0] = inflation
    namelist["assim_tools_nml"]["cutoff"] = localization
    namelist["obs_kind_nml"]["assimilate_these_obs_types"] = assimilatedVars
    writeNamelist(namelistPath)

    #Run the filter to produce the results
    subprocess.call("./filter", cwd=workPath)
    #Format the results nicely into RMSE and spread
    subprocess.call(["rm", "rms_spread_case"], cwd=workPath)
    #For this to work the matlab scripts associated with this experiment need to be in the matlab path
    p = subprocess.Popen(["matlab", "-nodesktop", "-nosplash", "-nodisplay"], stdin=subprocess.PIPE, cwd=workPath)
    p.communicate("prior_post")
    #Get the results and convert them into an array
    #This analysis is specific to the experiment
    with open(workPath + "rms_spread_case", "r") as resultsfile:
        results = resultsfile.read().replace(" ", "").split(",")[:-1]
    #Write data
    with open(datafile, "a") as data:
        data.write(",".join(
            [str(ensembleSize), 
            str(filterKind), 
            str(inflation), 
            str(localization), 
            assimilatedVars.replace(",", " and "), 
            "preassim.nc", 
            results[0], results[1], results[2], results[3]]
            )
        )
        data.write(",".join(
            [str(ensembleSize), 
            str(filterKind), 
            str(inflation), 
            str(localization), 
            assimilatedVars.replace(",", " and "), 
            "analysis.nc", 
            results[4], results[5], results[6], results[7]]
            )
        )


