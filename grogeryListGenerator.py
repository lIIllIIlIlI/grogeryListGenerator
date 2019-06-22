###################################################################################################
#                                Description                                                      #
#    Creates a grogery list from given meals and ingredience that will fit for given number of    #
#    days. The script will find at least as much kalories as needed for the given number of days  #
#    Furthermore it will pick only low carb meals if the respective input argument is given.      #            
#    To bring more variety, the script will try to pick meals at a random to generate differnt    #
#    result with every run                                                                        #
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
import argparse
import yaml

from pathlib import Path


###################################################################################################
#                                Input Arguments                                                  #
###################################################################################################
parser = argparse.ArgumentParser()

# define input options
parser.add_argument('--days', help = 'Number of days the grogerys should last', type = int, required = True)
parser.add_argument('--kcal', help = 'Number of calories required for a day without sport', type = int, required = True)
parser.add_argument('--nocarb','-n', help = 'Make the generator filter out high carb meals', action="store_true", default=False)
parser.add_argument('--workout', help='Number of workouts during the choosen period of time', type = int, default = False)
parser.add_argument('--cheatmeals', help='Number of meals that are taken outside during the choosen period', type = int, default = False)
parser.add_argument('--verbose', '-v', help='Show debug information', action="store_true", default = False)

args = parser.parse_args()

###################################################################################################
#                                Init Logger                                                      #
###################################################################################################

# create logger
loggerName = Path(__file__).stem
logFormatter = logging.Formatter(fmt=' %(name)s :: %(levelname)s :: %(message)s')
logger = logging.getLogger(loggerName)
logger.setLevel(logging.DEBUG)

# create console handler
Handler = logging.StreamHandler()
if(args.verbose):
        Handler.setLevel(logging.DEBUG)
else:
        Handler.setLevel(logging.INFO)
Handler.setFormatter(logFormatter)

# Add console handler to logger
logger.addHandler(Handler)

logger.info("*** Initialise input arguments: SUCCESS ***")
logger.info("*** Initialise logger: SUCCESS ***")

                    
###################################################################################################
#                                Global Variables                                                 #
###################################################################################################

# Path to meal list yaml config file
mealListFile = Path(__file__).parent / "mealList.yaml"

# Path to macro list yaml config file
macroListFile = Path(__file__).parent / "macroList.yaml"

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
        exit(1)
    else:
        logger.info("*** Checking the python version: SUCCESS ***")

    # check if both yaml config files exist
    if not (Path(mealListFile).is_file() and Path(macroListFile).is_file()):
        logger.error("Could not find yaml config files. Make sure mealList.yaml and macroList.yaml exist. Exiting ...")
        sys.exit(0)        
    

def readYamlFiles():
    """
    Reads both meal and macro config yaml files, stores the data in python dictionarys and 
    returns both.
    """    
    with open(macroListFile, 'r') as stream:
        try:
            macroList = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.error("*** Macro list is invalid. Reading the file gives the following error: {}. Exiting ...".format(exc))

    with open(mealListFile, 'r') as stream:
        try:
            mealList = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.error("*** Meal list is invalid. Reading the file gives the following error: {}. Exiting ...".format(exc))

    return mealList, macroList
    

def calculateKcalForMeals(mealList, macroList):
    """
    Resolves overall kcal number for all meals from the given macroLists and returns the 
    adapted mealList.
    """

    return mealList


def createGroceryList(mealList):
    """
    Creates a list of grocerys from the mealList that fulfull the requirements. Furthermore
    it adds up incredience that appear in more than one meal to not list the same ingredience 
    twice.
    """
    groceryList = {}

    return groceryList


def outputGroceryList(groceryList):
    """
    Outputs the generated grocery list via yaml file. Destination could be moved from yaml
    to google notes in the future.
    """


if __name__ == '__main__':

    # List of chosen grocerys
    groceryList = {}

    # dictionary of meals configured by user yaml files
    mealList = {}

    # dictionary of incredience to macros configured by user yaml files
    macroList = {}

    init()

    # Read user configured yaml files
    mealList, macroList = readYamlFiles()

    # Derive the macros and kcal for each meal
    calculateKcalForMeals(mealList, macroList)

    # Create a grocery list from given meals
    groceryList = createGroceryList(mealList)

    # Output generated grocery list to yaml file
    outputGroceryList(groceryList)

