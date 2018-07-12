'''
Code to automate running filters in DART
'''
#Imports
import f90nml #For parsing namelist files
import itertools #For iterating through all of the possible combinations
import netCDF4 #For reading the output files of the programs
import os #For messing with file system
import subprocess #For running the perfect_model_obs and filter code

#-----------------------------------------------------------------------------------
# RUN PARAMETERS
#-----------------------------------------------------------------------------------

#Set the path to the work directory of the model that is being used
workPath = "../../DART/concentration_observations/models/simple_advection/work/"
#Set the path to the namelist that controls the model inputs
namelistPath = workPath + "input.nml"

#Open the model namelist
namelist = f90nml.read(namelistPath)

#The list of ensemble sizes to check
ensembleSizes = [80]

#The list of filter kinds to check
#8: RHF
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
#for (ensembleSize, filterKind, inflation, localization, assimilatedVars) in itertools.product(ensembleSizes, filterKinds, inflations, localizations, assimilatedVarSets):
    #print(inflation)

#-----------------------------------------------------------------------------------
# FUNCTIONS
#-----------------------------------------------------------------------------------

#Write any changes to the name list into the actual file
def writeNamelist(path):
    #This is currently done by removing the file and creating a new one,
    #which could damage the namelist - use carefully
    #TODO: find a safer way to write namelists
    os.remove(path)
    namelist.write(path)

#Runs the perfect_model_obs and filter commands in a model's work directory
def runFilter(path):
    subprocess.call(path + "/perfect_model_obs")
    subprocess.call(path + "/filter")

