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
from random import choice

from Lib.helperFunctions import setLogger
from Lib.helperFunctions import getPrettyLogger
from Lib.helperFunctions import LOGMODUS
from Lib.helperFunctions import FILELOGGING
from Lib.helperFunctions import resolveDoubleEntries


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
logger = getPrettyLogger(loggerName, logLevel, FILELOGGING.INACTIVE)

logger.info("*** Initialise input arguments: SUCCESS ***\n")
logger.info("*** Initialise logger: SUCCESS ***\n")


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
#                                classes                                                          #
###################################################################################################

# class meal --------------------------------------------------------------------------------------
#
#   Meal object represents meal recipe with its nutrition
#   
#       watchList - list of additives to keep in stock for the meal 
#   
#       ingredientList - {
#                               ingredientObject: amount
#                               ingredientObject: amount
#                               ...
#                         }
#
#       options - several mutually exclusive meal variant options  
#               {
#                       {
#                               ingredientObject: amount
#                               ingredientObject: amount
#                               ...
#                       },  
#                       {
#                               ingredientObject: amount
#                               ingredientObject: amount
#                               ...
#                       }  
#                 }
#
#       kcal - overall kcal count of the meal
#
#       carb - overall carb count of the meal
#
#       protein - overall protein count of the meal
#
#       fat - overall fat count of the meal
#
# -------------------------------------------------------------------------------------------------

class meal:
    def __init__(self, name, ingredientDict, watchList, options):
        self.name = name
        self.ingredientDict = ingredientDict
        self.watchList = watchList
        self.options = options
        self.kcal = 0
        self.carb = 0
        self.protein = 0
        self.fat = 0

    def __repr__(self):
        """
        Overload __repr__ method to enable fancy printing and logger support on print operations.
        """
        mealDescriptionString = "\n"
        mealDescriptionString += "<class: " + self.__class__.__name__ + ",\n"
        mealDescriptionString += " name: " + str(self.name) + ",\n"
        mealDescriptionString += " ingrdients: " + str(self.ingredientList) + ",\n"
        mealDescriptionString += " watchList: " + str(self.watchList) + ",\n"
        mealDescriptionString += " macros (K|C|P|F): " + str(self.kcal) + " " + \
                                   str(self.carb) + " " + str(self.protein) + " " + \
                                   str(self.fat) + ",\n"
        mealDescriptionString += " watchList: " + str(self.watchList) + ",\n"
        mealDescriptionString += " watchList: " + str(self.watchList) + ",\n"
        mealDescriptionString += " name: " + str(self.name) + " >"
        return mealDescriptionString

# class meal --------------------------------------------------------------------------------------
#
#   Ingredient object represents the nutrition stats of the ingredient
#   
#       kcal - kcal count of the ingredient per metric
#
#       carb - carb count of the ingredient per metric
#
#       protein - protein count of the ingredient per metric
#   
#       fat - count of the ingredient per metric
#  
#       metric - measuring unit of the ingrdient, either "unit" or "gram"
#
# -------------------------------------------------------------------------------------------------

class ingredient:
    def __init__(self, name, kcal, carb, protein, fat, metric):
        self.name = name
        self.kcal = kcal
        self.carb = carb
        self.protein = protein
        self.fat = fat
        self.metric = metric

    def __repr__(self):
        """
        Overload __repr__ method to enable fancy printing and logger support on print operations.
        """
        ingredientDescriptionString = "\n"
        ingredientDescriptionString += "<class: " + self.__class__.__name__ + ",\n"
        ingredientDescriptionString += " name: " + str(self.name) + ",\n"
        ingredientDescriptionString += " macros (K|C|P|F): " + str(self.kcal) + " " + \
                                   str(self.carb) + " " + str(self.protein) + " " + \
                                   str(self.fat) + ",\n"
        ingredientDescriptionString += " metric: " + str(self.metric) + ">\n"
        return ingredientDescriptionString


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
        logger.info("*** Checking the python version: SUCCESS ***\n")
   
    # check if both yaml config files exist
    if not mealDictFile or not ingredientDictFile:
        logger.error("Could not find yaml config files. Make sure mealList.yaml exists here ({}) \
                      and ingredientList here: ({}). yaml exist. Exiting ...".format(Path(mealDictFile), \
                      Path(ingredientDictFile)))
        sys.exit(1)        
    
    # Init logger for helper functions
    setLogger(logger)

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

    logger.debug("ingredient dictionary:\n{}\n\n".format(yaml.dump(ingredientDict)))
    logger.debug("meal dictionary:\n{}\n\n".format(yaml.dump(mealDict)))
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
    logger.debug("\n\nList of meal objects after initialization:")
    for meal in mealObjectListInit:
        logger.debug(meal)

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

    logger.debug("\n\nList of ingredient objects after initialization:")
    for ingredient in ingredientObjectListInit:
        logger.debug(ingredient)

    return ingredientObjectListInit

def convertMealToObject(mealName, mealData, ingredientObjectList):
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
    mealObject = ""
    ingredientList = []

    if "options" in mealData:
        options = mealData['options']        
        del mealData['options']
    else:
        options = ""

    if "watchList" in mealData:
        watchList = mealData['watchList']        
        del mealData['watchList']
    else:
        watchList = ""

    # only ingredients left in mealData dictionary
    for ingredient in mealData:
        #TODO: Hier werden einfach nur die übrig gebliebnen key/value pairs übernommen. Es sollen aber die tatsächlichen ingredient objekte eingetragen werden
        ingredientList.append(ingredient)

    if isMealDataValid(ingredientDict, watchList, options, ingredientObjectList):
        mealObject = meal(mealName, ingredientDict, watchList, options)

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

def isMealDataValid(ingredientDict, watchList, options, ingredientObjectList):
    """
    Performs semantical check on the given meal data and return wether the data are valid.
    Performs the following checks:
        - All ingrdients in ingrdient list exist
        - All 
    """
    isIngredientValid = True


    #TODO: Implement me 
    return isIngredientValid

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


def resolveOptions(mealDict):        
    """
    The mealDict may contain different options for a single meal. This script parses all given 
    options, chooses the best fitting one and resolves the dictionary accordingly.
    #TODO: [FEATURE] Extract the best option, not just a random one
    """
    resolvedMealDict = {}

    logger.debug("resolvedMealDict:\n{}\n\n".format(yaml.dump(resolvedMealDict)))
    return resolvedMealDict


def splitMealDict(tmpMealDict):
    """
    Separates the watchlist from each meal and returns both parts autonomous.
    """
    for meal in tmpMealDict:
        print(meal)
    resolvedTmpMealDict = {}
    watchDict = {}

    logger.debug("Split up tmpMealDict:\n {}\n\n".format(yaml.dump(resolvedTmpMealDict)))
    logger.debug("watchDict:\n{}\n\n".format(yaml.dump(watchDict)))
    return resolvedTmpMealDict, watchDict


def generateMealingredientDict(mealDict, ingredientDict):
    """
    Creates and returns  a dictionary containing the ingredient nutritions for every meal listed
    in the meal dict.
    """
    mealIngredientDict = {}

    logger.debug("mealingredientDict:\n{}\n\n".format(yaml.dump(mealIngredientDict)))
    return mealIngredientDict


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
    groceryList = resolveDoubleEntries(tmpGroceryList)
    
    logger.debug("groceryList:\n{}\n\n".format(yaml.dump(groceryList)))
    return groceryList


def generateWatchList(watchDict, mealList):
    """
    watchDict contains the watch items for each meal and mealList the chose meals. 
    The function will create a list of watch items for the chosen meals and return ist.
    """
    watchList = []
    
    logger.debug("watchList:\n{}\n\n".format(yaml.dump(watchList)))
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
    logger.info("*** Prepare data ***\n")
    # Create resolvedMealDict and mealingredientDict ---------------------------------------------------
    # Read user configured yaml files
    mealDict, ingredientDict = readYamlFiles()

    # create fully resolved ingrdient object list
    ingredientObjectList = generateIngredientObjectList(ingredientDict)

    # create initial (unresolved) meal object list
    mealObjectListInit = generateMealObjectList(mealDict, ingredientObjectList)

    # Resolve options in meal list
    tmpMealDict = resolveOptions(mealDict)

    # Split meals and watch items convertDictToObjects
    tmpMealDict, watchDict = splitMealDict(tmpMealDict)

    # Generate a dict that stores ingredients for every meal
    mealingredientDict = generateMealingredientDict(mealDict, ingredientDict)

    # Filter non lowcarb meals
    if args.lowcarb:
        resolvedMealDict = lowCarbFilter(tmpMealDict, mealingredientDict)
    else:
        resolvedMealDict = tmpMealDict
    # ---------------------------------------------------------------------------------------------

    # Create final results ------------------------------------------------------------------------
    logger.info("*** Generating results ***\n")

    mealList = chooseMeals(resolvedMealDict)    

    # Create a grocery list from choosen meals
    groceryList = generateGroceryList(mealList, resolvedMealDict)
 
    watchList = generateWatchList(watchDict, mealList)
    # ---------------------------------------------------------------------------------------------

    # Output generated grocery list to yaml file
    outputResults(mealList, groceryList, watchList)

