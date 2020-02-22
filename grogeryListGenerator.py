###################################################################################################
#                                Description                                                      #
#    Creates a grogery list from given meals and ingredience that will fit for given number of    #
#    days. The script will find at least as much kalories as needed for the given number of days  #
#    Furthermore it will pick only low carb meals if the respective input argument is given.      #            
#    To bring more variety, the script will try to pick meals at a random to generate differnt    #
#    result with every run.                                                                       #
#                                                                                                 #
#   Feature Ideas:                                                                                #  
#                                                                                                 #  
#                                                                                                 #  
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
import copy
import random

from argparse import ArgumentParser
from pathlib import Path
from enum import Enum

from Lib.prettyLogger import getPrettyLogger
from Lib.prettyLogger import LOGMODUS
from Lib.prettyLogger import FILELOGGING

from Lib.helperFunctions import *

from Class.meal import meal
from Class.ingredient import ingredient


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
parser.add_argument('--lowcarb', help = 'Make the generator filter out high carb meals', \
                    action="store_true", default=False)
parser.add_argument('--keto', help = 'Make the generator filter out carb meals', \
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
logger = getPrettyLogger(loggerName, logLevel, FILELOGGING.INACTIVE)
resultLogger = getPrettyLogger("groceryList", LOGMODUS.VERBOSE, FILELOGGING.ACTIVE)


###################################################################################################
#                                Global Variables                                                 #
###################################################################################################

# Path to meal list yaml config file
mealDictFile = Path.cwd() / "Config" / "mealList.yaml"

# Path to ingredient list yaml config file
ingredientDictFile = Path.cwd() / "Config" / "ingredientList.yaml"

# List of ingredients extracted from yaml
ingredientList = []

# List of meals extracted from yaml
mealList = []

# List of chosen meals
choosenMealList = []

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
#                                private classes                                                  # 
###################################################################################################

# Kcal per carb treshold
class TRESHOLD(Enum):
    LOWCARB = 8
    KETO = 3

###################################################################################################
#                                private functions                                                # 
###################################################################################################

def initialize():
    """
    The init functions performs a couple of initialization and checks.
    """ 
    checkInputArgs(args)
    checkPythonVersion()
    checkConfigFileExist(mealDictFile, ingredientDictFile)
    registerLoggers(logger)


def readYamlFiles():
    """
    Reads both meal and ingredient config yaml files, stores the data in python dictionarys and 
    returns both.

    Meal yaml: 
                Meal1 {
                        ingredient1: amount,
                        ingredient2: amount,
                        ingredient3: amount,
                        ingredient4 ...
                        option: {
                                    item1: amount,
                                    item2: amount
                                },
                                {
                                    item3: amount,
                                    item4: amount
                                } (optional)
                        watchList: [item1, item2, item3] (optional)
                    },
            
                Meal2 ...

    ingredient yaml:
                Ingredient1 {
                                carbs: amount,
                                fat: amount,
                                protein: amount,
                                kcal: amount,
                                metric: {gram, unit} (optional)
                            },
                
                Ingredient2 ...
    
    """    
    with open(ingredientDictFile, 'r') as stream:
        try:
            ingredientDict = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.error("*** ingredient list is invalid. Reading the file gives the following error: \
                          {}. Exiting ...".format(exc))

    with open(mealDictFile, 'r') as stream:
        try:
            mealDict = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.error("*** Meal list is invalid. Reading the file gives the following error: \
                          {}. Exiting ...".format(exc))

    return mealDict, ingredientDict


def generateMealObjectList(mealDict, ingredientObjectList):
    """
    Generates and returns a list of meal objects from the given meal dictionary.

    input: dictionary
        Meal1 {
                    ingredient1: amount,
                    ingredient2: amount,
                    ingredient3: amount,
                    ingredient4 ...
                    option: {
                                item1: amount,
                                item2: amount
                            },
                            {
                                item3: amount,
                                item4: amount
                            } (optional)
                    watchList: [item1, item2, item3] (optional)
                    },
    
        Meal2 ...

    output: list of objects of class meal 
    """
    mealObjectListInit = []

    # Conversion
    for mealName, mealData in mealDict.items():
        mealObject = convertMealToObject(mealName, mealData, ingredientObjectList)
        # make sure an object was created
        if mealObject:
            mealObjectListInit.append(mealObject)

    # error handling
    if not mealObjectListInit:
        logger.error("No valid meals could be created from the meal yaml file. Please check your config files. Terminating ...")
        sys.exit(1)

    # add debug information
    mealNames = [meal.name for meal in mealObjectListInit]
    logger.info("Extracted meals: \n{}".format(yaml.dump(mealNames)))

    return mealObjectListInit


def generateIngredientObjectList(ingredientDict):
    """
    Generates and returns a list of ingredient objects from the given ingredient dictionary.

    input: dictionary
        Ingredient1 {
                        carbs: amount,
                        fat: amount,
                        protein: amount,
                        kcal: amount,
                        metric: {gram, unit} (optional)
                    },
                
        Ingredient2 ...

    output: list of objects of class ingredient
    """
    ingredientObjectListInit = []

    for ingredientName, ingredientData in ingredientDict.items():
        ingredientObject = convertIngredientToObject(ingredientName, ingredientData)
        if ingredientObject:
            ingredientObjectListInit.append(ingredientObject)

    if not ingredientObjectListInit:
        logger.error("No valid ingredients could be created from the ingredient yaml file. Please check your config files. Terminating ...")
        sys.exit(1)

    return ingredientObjectListInit


def lowCarbFilter(mealDict, mealingredientDict):
    """
    Function filters every meal that has more than 50g of carbs for every 1000 Kcal
    """
    # for meal in mealList:
       # for ingredience 
    lowCarbMealDict = {}

    logger.debug("lowCarbMealDict:\n{}\n\n".format(yaml.dump(lowCarbMealDict)))
    return lowCarbMealDict

def resolveMealList(mealObjectList):
    for meal in list(mealObjectList):
        meal.resolveMacros()
    return mealObjectList

def applyLowcarbFilter(mealObjectList):
    """
    Filters non lowcarb meals from the given list and returns the reduced list.
    Lowcarb meals have a kcal to carb ratio that exceed the defined treshold.
    """
    lowCarbMealObjectList = []
    filteredMealNames = []
    for meal in mealObjectList:
        if meal.kcal / meal.carb > TRESHOLD.LOWCARB:
            lowCarbMealObjectList.append(meal)
        else:
            filteredMealNames.append(meal.name)
    logger.info("Meals removed by lowcarb filter: \n{}".format(yaml.dump(filteredMealNames)))
    return lowCarbMealObjectList


def applyKetoFilter(mealObjectList):
    """
    Filters non keto meals from the given list and returns the reduced list.
    Lowcarb meals have a kcal to carb ratio that exceed the defined treshold.
    """
    ketoMealObjectList = []
    filteredMealNames = []
    for meal in mealObjectList:
        if meal.kcal / meal.carb > TRESHOLD.LOWCARB:
            ketoMealObjectList.append(meal)
        else:
            filteredMealNames.append(meal.name)
    logger.info("Meals removed by lowcarb filter: \n{}".format(yaml.dump(filteredMealNames)))
    return ketoMealObjectList

def chooseMeals(mealList):
    """
    Randomly chooses meals from the given meal list until the target kcal count is reached. 
    The tolerated kcal deviation in both directions is 200 Kcal. The function tries to meet
    this requirement.
    """
    mealListCopy = list(mealList)
    choosenMealList = []
    targetKcal = args.days * args.kcal
    currentKcal = 0

    while currentKcal > targetKcal - 200:
        choosenMeal = random.choice(mealListCopy)
        choosenMealList.append(choosenMeal)
        currentKcal += choosenMeal.kcal
        mealListCopy.remove(choosenMeal)
        if not mealListCopy:
            logger.error("Not enough meals specified to meet the given amounts of days and kcal without repetition")
            sys.exit(1)
    if currentKcal - targetKcal > 200:
        choosenMealList = improveChoosenMealList(mealList, choosenMealList)

    return choosenMealList

def generateGroceryList(mealList): 
    """
    Generates and returns the final grocery list by looking up and adding the proper amount 
    of every ingrdient for each chose meal.
    #TODO [FEATURE] The grocery list currently contains duplicates. Merge those duplicates
    """
    groceryList = []
    for meal in mealList:
        groceryList.append(meal.ingredientList)
    return groceryList

def outputResults(choosenMealList, groceryObjectList):
    """
    Outputs the generated results
    #TODO [FEATURE] Create the option to print output to google docs instead of local file
    """
    mealNames = [meal.name for meal in mealList]
    ingredientNameList = [ingredient.name for ingredient in groceryObjectList]
    amountList = [ingredient.amount for ingredient in groceryObjectList]

    groceryList = zip(ingredientNameList, amountList)

    resultLogger.info("Choosen meals: {}\n".format(mealNames))
    resultLogger.info("Grocery list: {}\n".format(groceryList))
    return


###################################################################################################
#                                Driver                                                           # 
###################################################################################################
if __name__ == '__main__':

    logger.info("*** initialize ***")
    initialize()

    logger.info("*** Read yaml config files ***")
    mealDict, ingredientDict = readYamlFiles()

    logger.info("*** create initial meal list ***")
    ingredientObjectListInit = generateIngredientObjectList(ingredientDict)

    mealObjectListInit = generateMealObjectList(mealDict, ingredientObjectListInit)


    logger.info("*** calculate macro nutrition of each meal ***")
    mealObjectListResolved = resolveMealList(mealObjectListInit)

    if args.keto:
        logger.info("*** apply keto filter on meal list  ***")
        mealObjectFilteredList = applyKetoFilter(mealObjectListResolved)
    elif args.lowcarb:
        logger.info("*** apply lowcarb filter on meal list  ***")
        mealObjectFilteredList = applyLowcarbFilter(mealObjectListResolved)
    else:
        mealObjectFilteredList = mealObjectListResolved

    logger.info("*** create meal plan  ***\n")
    choosenMealList = chooseMeals(mealObjectFilteredList)    

    logger.info("*** create grocery list ***\n")
    groceryList = generateGroceryList(choosenMealList)

    logger.info("*** generate output ***\n")
    outputResults(choosenMealList, groceryList)

