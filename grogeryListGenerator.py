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
import copy
import random

from argparse import ArgumentParser
from pathlib import Path
from enum import Enum

from Lib.prettyLogger import getPrettyLogger
from Lib.prettyLogger import LOGMODUS
from Lib.prettyLogger import FILELOGGING

from Lib.helperFunctions import *

from meal import meal
from ingredient import ingredient


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



def getValueFromDictionary(dictionary, dictionaryName, key):
    """
    Gets value for given key from given dictionary.
    Returns None if key could not be found in dictionary.
    """
    if key in dictionary:
        value = dictionary[key]
    else:
        logger.warning('Ingredient {} contains no {} value and will be ignored'.format(dictionaryName, key))
        value = None
    return value

def getIngredientObject(ingredientObjectList, ingredientName):
    """
    Tries to extract and return the requested ingredient from ingredientObjectList. Returns
    None if requested ingredient could not be found. 
    """
    requestedObject = None
    for ingredientObject in ingredientObjectList:
        if ingredientObject.name == ingredientName:
            requestedObject = ingredientObject
    
    return requestedObject

def convertMealToObject(mealName, mealData, IngredientObjectList):
    """
    Converts the dictionary meal into an object of meal class.

    Input: dict
        ingredient1: amount,
        ingredient2: amount,
        ingredient3: amount,
        ingredient4: amount
        options: {
                    item1: amount,
                    item2: amount
                },
                {
                    item3: amount,
                    item4: amount
                } (optional)
        watchList: [item1, item2, item3] (optional)

    output: object class meal
    """
    mealObject = None
    ingredientList = []
    resolveStatus = True

    # catch and handle options
    if "options" in mealData:
        options = convertOptionsToIngredientList(mealData['options'],IngredientObjectList)  
        if options == []:
            logger.error("Meal {} could not be resolved because given options could not be resolved. Please adapt the yaml config".format(mealName))

        mealData.update(options)
        del mealData['options']
    else:
        options = None

    # catch and handle watchList
    if "watchList" in mealData:
        watchList = mealData['watchList']        
        del mealData['watchList']
    else:
        watchList = ""

    # catch and handle everything else which should only be ingrdients
    for ingredient in mealData.keys():
        ingredientObject = getIngredientObject(IngredientObjectList, ingredient)
        if ingredientObject:
            ingredientObject.amount = mealData[ingredient]
            ingredientList.append(ingredientObject)
        else:
            logger.warning("Meal {} could not be resolved because ingredient {} in not be found in the ingredient list.".format(mealName, ingredientObject.name))
            resolveStatus = False

    if resolveStatus:
        mealObject = meal(mealName, watchList, options, ingredientList)

    return mealObject

def convertIngredientToObject(ingredientName, ingredientData):
    """
    Converts the dictionary ingredient into an object of ingredient class. It catches 
    and handles incomplete or ivalid ingredient data.
    
    Input: dictionary
        carbs: amount
        fat: amount
        protein: amount
        kcal: amount
        metric: {gram, unit} (optional)

    output: object class ingredient
    """
    ingredientObject = ""

    # extract parameters of given ingredient
    name = ingredientName
    kcal = getValueFromDictionary(ingredientData, ingredientName, "kcal")
    carbs = getValueFromDictionary(ingredientData, ingredientName, "carbs")
    fat = getValueFromDictionary(ingredientData, ingredientName, "fat")
    protein = getValueFromDictionary(ingredientData, ingredientName, "protein")

    # extract metric, use default if not existing
    if 'metric' in ingredientData:
        metric = ingredientData['metric']
    else:
        metric = "gram"

    # create object if extracted ingredient data are valid
    if isIngredientDataValid(kcal, carbs, protein, fat, metric, ingredientName):
        ingredientObject = ingredient(name, int(kcal), int(carbs), int(protein), int(fat), metric)

    return ingredientObject

def isIngredientDataValid(kcal, carbs, protein, fat, metric, ingredientName):
    """
    Performs semantical check on the given ingredient data and return wether the data are valid.
    """
    isIngredientValid = True
    if (kcal is None) or (carbs is None) or (fat is None) or (protein is None):   
        isIngredientValid = False       

    if kcal == 0:
        logger.warning('Ingredient {} contains 0 kcal which is considered an error and therefore will be ignored'.format(ingredientName))
        isIngredientValid = False

    if not isinstance(kcal, int):
        if not kcal.isdigit(): 
            isIngredientValid = False
            logger.warning('The value "{}" of Ingredient {} contains invalid characters. Ingredient will be ignored'.format(kcal, ingredientName))

    if not isinstance(carbs, int):
        if not carbs.isdigit(): 
            isIngredientValid = False
            logger.warning('The value "{}" of Ingredient {} contains invalid characters. Ingredient will be ignored'.format(carbs, ingredientName))

    if not isinstance(fat, int):
        if not fat.isdigit(): 
            isIngredientValid = False
            logger.warning('The value "{}" of Ingredient {} contains invalid characters. Ingredient will be ignored'.format(fat, ingredientName))

    if not isinstance(protein, int):
        if not protein.isdigit(): 
            isIngredientValid = False
            logger.warning('The value "{}" of Ingredient {} contains invalid characters. Ingredient will be ignored'.format(protein, ingredientName))

    return isIngredientValid

def convertOptionsToIngredientList(optionsDict, IngredientObjectList):
    """
    Converts a dictionary of ingredient options into a list of list of ingredient objects

    Input:
    optionsDict = {
        {
            ingredientName1: amount,
            ingredientNam2: amount,
            ...
        },
        {
            ingredientName1: amount,
            ...
        },
        ...
    }

    output:
    optionsDict = [
        [ingredient1, ingredient2, ..], [ingredient1, ...]
    ]
    """
    resolvedOption = []
    option = getRandomOption(optionsDict)
    for optionIngredient in option:
        optionIngredientObject = getIngredientObject(IngredientObjectList, optionIngredient)
        if optionIngredientObject:
            optionIngredientObject.amount = option[optionIngredient]
            resolvedOption.append(optionIngredientObject)
        else:
            option = []
            break
    return option

def getRandomOption(options):
    return random.choice(options)

def lowCarbFilter(mealDict, mealingredientDict):
    """
    Function filters every meal that has more than 50g of carbs for every 1000 Kcal
    """
    # for meal in mealList:
       # for ingredience 
    lowCarbMealDict = {}

    logger.debug("lowCarbMealDict:\n{}\n\n".format(yaml.dump(lowCarbMealDict)))
    return lowCarbMealDict


def chooseMeals(resolvedMealDict):
    """
    Picks a list of meals that fit the kcal requirements.
    Currently, it will pick meals at random and stop once the kcal goal is reached.
    TODO: Store results of last run and change probabilities of meals picked that run 
    to support variety
    TODO: Try to match the kcal goal as close as possible instead of simply adding items 
    """
    mealList = []

    logger.debug("mealList:\n{}\n\n".format(yaml.dump(mealList)))
    return mealList


def generateGroceryList(mealList, mealDict): 
    """
    Generates and returns the final grocery list by looking up and adding the proper amount 
    of every ingrdient for each chose meal.
    """
    tmpGroceryList = {}


    logger.debug("Unresolved groceryList:\n{}\n\n".format(yaml.dump(tmpGroceryList)))
    # get rid of double entries in grocery dict
    
    logger.debug("groceryList:\n{}\n\n".format(yaml.dump(groceryList)))
    return groceryList

def outputResults(mealList):
    """
    Outputs the generated results
    #TODO [FEATURE] Implement file output option
    """
    
    return

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

def resolveMealList(mealObjectList):
    for meal in list(mealObjectList):
        meal.resolveMacros()
    return mealObjectList

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

    # filter
    if args.keto:
        logger.info("*** apply keto filter on meal list  ***")
        mealObjectFilteredList = applyKetoFilter(mealObjectListResolved)
    elif args.lowcarb:
        logger.info("*** apply lowcarb filter on meal list  ***")
        mealObjectFilteredList = applyLowcarbFilter(mealObjectListResolved)
    else:
        mealObjectFilteredList = mealObjectListResolved


    sys.exit(1)

    # create meal plan
    logger.info("*** create meal plan  ***\n")

    mealList = chooseMeals(mealObjectFilteredList)    

    # Output results
    logger.info("*** output results  ***\n")

    outputResults(mealList)

