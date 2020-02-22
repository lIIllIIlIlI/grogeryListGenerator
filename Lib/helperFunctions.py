import logging
import sys
import random

from pathlib import Path

from Class.ingredient import registerIngredientLogger
from Class.ingredient import ingredient
from Class.meal import registerMealLogger
from Class.meal import meal


logger = logging.getLogger(__name__) 

def registerHelperFunctionsLogger(Logger):
    global logger
    logger = Logger


def registerLoggers(logger):
    registerMealLogger(logger)
    registerIngredientLogger(logger)
    registerHelperFunctionsLogger(logger)

def checkConfigFileExist(mealDictFile, ingredientDictFile):
    if not mealDictFile or not ingredientDictFile:
        logger.error("Could not find yaml config files. Make sure mealList.yaml exists here ({}) \
                      and ingredientList here: ({}). yaml exist. Exiting ...".format(Path(mealDictFile), \
                      Path(ingredientDictFile)))
        sys.exit(1)     

def checkInputArgs(args):
    if args.lowcarb and args.keto:
        logger.warning("Lowcarb option has no effect when keto option is set")

def checkPythonVersion():
    # Check if Python >= 3.5 is installed
    if sys.version_info < (3, 5, 0):
        sys.stderr.write("You need Python 3.5 or greater to run this script \n")
        sys.exit(1)

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

def improveChoosenMealList(mealList, choosenMealList):
    return choosenMealList