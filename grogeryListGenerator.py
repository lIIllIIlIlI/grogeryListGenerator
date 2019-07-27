###################################################################################################
#                                Description                                                      #
#    Creates a grogery list from given meals and ingredience that will fit for given number of    #
#    days. The script will find at least as much kalories as needed for the given number of days  #
#    Furthermore it will pick only low carb meals if the respective input argument is given.      #            
#    To bring more variety, the script will try to pick meals at a random to generate differnt    #
#    result with every run.                                                                       #
#                                                                                                 #            
#    Author: Lukas                                                                                #
#                                                                                                 #
#    Contact: Github                                                                              #   
#                                                                                                 #
###################################################################################################


###################################################################################################
#                                Imports                                                          #
###################################################################################################
import logging
import sys
import yaml

from argparse import ArgumentParser
from pathlib import Path
from enum import Enum

from helperFunctions import setLogger
from helperFunctions import getPrettyLogger
from helperFunctions import LOGMODUS
from helperFunctions import FILELOGGING
from helperFunctions import resolveDoubleEntries

###################################################################################################
#                                Input Arguments                                                  #
###################################################################################################
# create parser object
parser = ArgumentParser()

# define input options
parser.add_argument('--days', help = 'Number of days the grogerys should last', type = int, \
                    required = True)
parser.add_argument('--kcal', help = 'Number of calories required for a day without sport', \
                    type = int, required = True)
parser.add_argument('--lowcarb','-n', help = 'Make the generator filter out high carb meals', \
                    action="store_true", default=False)
parser.add_argument('--workout', help='Number of workouts during the choosen period of time', \
                    type = int, default = False)
parser.add_argument('--cheatmeals', help='Number of meals that are taken outside during the \
                     choosen period', type = int, default = False)
parser.add_argument('--verbose', '-v', help='Show debug information', action="store_true", \
                     default = False)
parser.add_argument('--quiet', '-q', help='Show minimalistic output', action="store_true", \
                     default = False)

# read input
args = parser.parse_args()


###################################################################################################
#                                   Logger                                                        #
###################################################################################################

if(args.verbose):
    logLevel = LOGMODUS.VERBOSE
elif(args.quiet):
    logLevel = LOGMODUS.QUIET
elif(args.verbose and args.quiet):
    logLevel = LOGMODUS.NORMAL
    print("Options quiet and verbose are mutually exclusive. I will continue ignoring both inputs")
else:
    logLevel = LOGMODUS.NORMAL

loggerName = Path(__file__).stem
logger = getPrettyLogger(loggerName, LOGMODUS.NORMAL, FILELOGGING.INACTIVE)

logger.info("*** Initialise input arguments: SUCCESS ***")
logger.info("*** Initialise logger: SUCCESS ***")

                    
###################################################################################################
#                                Global Variables                                                 #
###################################################################################################

# Path to meal list yaml config file
mealDictFile = Path(__file__).parent / "mealList.yaml"

# Path to macro list yaml config file
macroDictFile = Path(__file__).parent / "macroList.yaml"

# dictionary of incredience to macros configured by user yaml files -------------------------------
#
#   incredience1 {
#                    kcal: #kcal,
#                    carbs: #carbs,
#                    protein: #protein,
#                    fat: #fat,
#                    metric: {'unit', 'weight'}
#                 }
#
#   incredience2 ...
#
# Note: Metric determines if given values are for an item or 100g
# -------------------------------------------------------------------------------------------------
macroDict = {}

# dictionary of meals given by yaml file-----------------------------------------------------------
#
#   Meal1 {
#               ingredient1: amount,
#               ingredient2: amount,
#               ingredient3: amount,
#               ingredient4: amount
#               option: {
#                           item1: amount,
#                           item2: amount
#                       },
#                       {
#                           item3: amount,
#                           item4: amount
#                       }
#               watchList: [item1, item2, item3]
#         },
#
#   Meal2 ...
#
# -------------------------------------------------------------------------------------------------
mealDict = {}

# dictionary of meals with resolved options and removed watchlsit ---------------------------------
#
#   Meal1 {
#               ingredient1: amount,
#               ingredient2: amount,
#               ingredient3: amount,
#               ingredient4: amount,
#         }, 
#
#   Meal2 ...
#
# -------------------------------------------------------------------------------------------------
resolvedMealDict = {}

# dictionary of meals given by yaml file-----------------------------------------------------------
#
#   Meal1[item1, item2, ...],
#
#   Meal2[ ...
#
# -------------------------------------------------------------------------------------------------
watchDict = {}

# dictionary of macros for each meal --------------------------------------------------------------
#
#   Meal1 {
#               kcal: #kcal,
#               carbs: #carbs,
#               protein: #protein,
#               fat: #fat,
#               watchList: [item1, item2, item3]
#         },
#
#   Meal2 ...
#
# -------------------------------------------------------------------------------------------------
mealMacroDict = {}

# List of chosen meals
mealList = []

# Watch items for chosen meals 
watchList = []

# List of dicts of chosen grocerys -------------------------------------------------------------------
#
#   item1: amount,
#
#   item2: ...
#
# -------------------------------------------------------------------------------------------------
groceryList = {}

###################################################################################################
#                                Functions                                                        # 
###################################################################################################

def init():
    """
    The init functions performs a couple of initialization and checks.
    """ 
    # Check if Python >= 3.5 is installed
    if sys.version_info < (3, 5, 0):
        sys.stderr.write("You need Python 3.5 or greater to run this script \n")
        sys.exit(1)
    else:
        logger.info("*** Checking the python version: SUCCESS ***")

    # check if both yaml config files exist
    if not (Path(mealDictFile).is_file() and Path(macroDictFile).is_file()):
        logger.error("Could not find yaml config files. Make sure mealList.yaml and macroList. \
                      yaml exist. Exiting ...")
        sys.exit(1)        
    
    # Init logger for helper functions
    setLogger(logger)

def readYamlFiles():
    """
    Reads both meal and macro config yaml files, stores the data in python dictionarys and 
    returns both.
    """    
    with open(macroDictFile, 'r') as stream:
        try:
            macroDict = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.error("*** Macro list is invalid. Reading the file gives the following error: \
                          {}. Exiting ...".format(exc))

    with open(mealDictFile, 'r') as stream:
        try:
            mealDict = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.error("*** Meal list is invalid. Reading the file gives the following error: \
                          {}. Exiting ...".format(exc))

    logger.debug("macro dictionary: {}".format(yaml.dump(macroDict)))
    logger.debug("meal dictionary: {}".format(yaml.dump(mealDict)))
    return mealDict, macroDict


def resolveOptions(mealDict):
    """
    Chooses one of every given option 
    """
    resolvedMealDict = {}

    logger.debug("resolvedMealDict: {}".format(yaml.dump(resolvedMealDict)))
    return resolvedMealDict


def splitMealDict(tmpMealDict):
    """
    Separates the watchlist from each meal and returns both parts autonomous.
    """
    resolvedTmpMealDict = {}
    logger.debug("Split up tmpMealDict: {}".format(yaml.dump(resolvedTmpMealDict)))
    logger.debug("watchDict: {}".format(yaml.dump(watchDict)))
    return resolvedTmpMealDict, watchDict


def generateMealMacroDict(mealDict, macroDict):
    """
    Creates and returns  a dictionary containing the macro nutritions for every meal listed
    in the meal dict.
    """
    mealMacroDict = {}

    logger.debug("mealMacroDict: {}".format(yaml.dump(mealMacroDict)))
    return mealMacroDict


def lowCarbFilter(mealDict, mealMacroDict):
    """
    Function filters every meal that has more than 50g of carbs for every 1000 Kcal
    """
    # for meal in mealList:
       # for ingredience 
    lowCarbMealDict = {}

    logger.debug("lowCarbMealDict: {}".format(yaml.dump(lowCarbMealDict)))
    return lowCarbMealDict


def chooseMeals(resolvedMealDict):
    """
    Picks a list of meals that fit the kcal requirements.
    Currently, it will pick meals at random and stop once the kcal goal is reached.
    TODO: Store results of last run and change probabilities of meals picked that run 
    to support variety
    TODO: Try to match the kcal goal as close as possible instead of simply adding items 
    """
    logger.debug("mealList: {}".format(yaml.dump(mealList)))
    return mealList


def generateGroceryList(mealList, mealDict): 
    """
    Generates and returns the final grocery list by looking up and adding the proper amount 
    of every ingrdient for each chose meal.
    """
    tmpGroceryList = {}


    logger.debug("Unresolved groceryList: {}".format(yaml.dump(tmpGroceryList)))
    # get rid of double entries in grocery dict
    groceryList = resolveDoubleEntries(tmpGroceryList)
    
    logger.debug("groceryList: {}".format(yaml.dump(groceryList)))
    return groceryList


def generateWatchList(watchDict, mealList):
    """
    watchDict contains the watch items for each meal and mealList the chose meals. 
    The function will create a list of watch items for the chosen meals and return ist.
    """
    
    logger.debug("watchList: {}".format(yaml.dump(watchList)))
    return watchList


def outputResults(mealList, groceryList, watchList):
    """
    Outputs the generated results
    #TODO [FEATURE] Implement file output option
    """
    
    return


###################################################################################################
#                                Driver                                                           # 
###################################################################################################
if __name__ == '__main__':
    #TODO [FEATURE] Support of Pre and Postworkout meals

    init()

    # Create resolvedMealDict and mealMacroDict ---------------------------------------------------
    # Read user configured yaml files
    mealDict, macroDict = readYamlFiles()

    # Resolve options in meal list
    tmpMealDict = resolveOptions(mealDict)

    # Split meals and watch items 
    tmpMealDict, watchDict = splitMealDict(tmpMealDict)

    # Generate a dict that stores macros for every meal
    mealMacroDict = generateMealMacroDict(mealDict, macroDict)

    # Filter non lowcarb meals
    if args.lowcarb:
        resolvedMealDict = lowCarbFilter(tmpMealDict, mealMacroDict)
    else:
        resolvedMealDict = tmpMealDict
    # ---------------------------------------------------------------------------------------------


    # Create mealList, groceryList and watchList ---------------------------------------------------
    mealList = chooseMeals(resolvedMealDict)

    # Create a grocery list from given meals
    groceryList = generateGroceryList(mealList, resolvedMealDict)

    watchList = generateWatchList(watchDict, mealList)
    # ---------------------------------------------------------------------------------------------


    # Output generated grocery list to yaml file
    outputResults(mealList, groceryList, watchList)

