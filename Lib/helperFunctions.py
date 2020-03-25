import logging
import sys
import random
import yaml

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

def checkConfigFileExist(configFiles):
    for configFile in configFiles:
        if not configFile:
            logger.error("Config file {} is missing. Exiting ...".format(configFile))
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
        options: 
                [
                    [
                        item1: amount,
                        item2: amount
                    ],
                    [
                        item3: amount,
                        item4: amount
                    ],
                    ...
                ] (optional)
        watchList: [item1, item2, item3] (optional)

    output: object class meal
    """
    mealObject = None
    ingredientList = []
    resolveStatus = True

    # catch and handle options
    if "options" in mealData:
    
        # TODO: [REFACTORING] mealData is a dictionary with "key": "amount" pairs. After removing the special keys, the rest
        #       of the key value pairs is converted to object. Therefore, this part should append the choosen option(s) to
        #       mealData and let the routine resolve it later on. Unfortunately, it currently already creates objects and adds
        #       them to the final object list. That makes the object flow hard to understand. Extending the functionality 
        #       was even hard for me as the original author of the code.
        
        # every option is resolved individually
        for option in mealData['options']:
            choosenIngredients = convertOptionToIngredientList(option, IngredientObjectList)  
            if choosenIngredients == []:
                logger.error("Meal {} could not be resolved because given options could not be resolved. Please adapt the yaml config".format(mealName))
                sys.exit(1)
            ingredientList.extend(choosenIngredients)
        del mealData['options']

    # catch and handle watchList
    if "watchList" in mealData:
        watchList = mealData['watchList']        
        del mealData['watchList']
    else:
        watchList = ""

    if "optional" in mealData:
        coinFlip = random.randint(0,1)
        if(coinFlip):
            for key, value in enumerate(mealData["optional"]):
                mealData[key] = value
        del mealData['optional']
        
    # catch and handle pre workout tag
    if "postWorkout" in mealData:
        postWorkout = True        
        del mealData['postWorkout']
    else:
        postWorkout = False

    # catch and handle post workout tag
    if "preWorkout" in mealData:
        preWorkout = True        
        del mealData['preWorkout']
    else:
        preWorkout = False

    # catch and handle everything else which should only be ingrdients
    for ingredient in mealData.keys():
        ingredientObject = getIngredientObject(IngredientObjectList, ingredient)
        if ingredientObject:
            ingredientObject.amount = mealData[ingredient]
            ingredientList.append(ingredientObject)
        else:
            logger.warning("Meal {} could not be resolved because ingredient {} in not be found in the ingredient list.".format(mealName, ingredient))
            resolveStatus = False

    if resolveStatus:
        mealObject = meal(mealName, watchList, postWorkout, preWorkout, ingredientList)

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

    # create object if extracted ingredient data are valid
    if isIngredientDataValid(kcal, carbs, protein, fat, ingredientName):
        ingredientObject = ingredient(name, int(kcal), int(carbs), int(protein), int(fat))

    return ingredientObject

def getValueFromDictionary(dictionary, dictionaryName, key):
    """
    Gets value for given key from given dictionary.
    Returns None if key could not be found in dictionary.
    """
    try:
        if key in dictionary:
            value = dictionary[key]
        else:
            logger.warning('Ingredient {} contains no {} value and will be ignored'.format(dictionaryName, key))
            value = None
    except:
        print(key)
        print("\n\n")
        print(dictionary)
        print("\n\n")
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

def isIngredientDataValid(kcal, carbs, protein, fat, ingredientName):
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
        if not is_number(kcal): 
            isIngredientValid = False
            logger.warning('The value "{}" of Ingredient {} contains invalid characters. Ingredient will be ignored'.format(kcal, ingredientName))

    if not isinstance(carbs, int):
        if not is_number(carbs): 
            isIngredientValid = False
            logger.warning('The value "{}" of Ingredient {} contains invalid characters. Ingredient will be ignored'.format(carbs, ingredientName))

    if not isinstance(fat, int):
        if not is_number(fat): 
            isIngredientValid = False
            logger.warning('The value "{}" of Ingredient {} contains invalid characters. Ingredient will be ignored'.format(fat, ingredientName))

    if not isinstance(protein, int):
        if not is_number(protein): 
            isIngredientValid = False
            logger.warning('The value "{}" of Ingredient {} contains invalid characters. Ingredient will be ignored'.format(protein, ingredientName))

    return isIngredientValid

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def convertOptionToIngredientList(optionsList, IngredientObjectList):
    """
    Converts a dictionary of ingredient options into a list of list of ingredient objects

    Input:
        optionsList: 
                [
                    [
                        item1: amount,
                        item2: amount
                    ],
                    [
                        item3: amount,
                        item4: amount
                    ],
                    ...
                ] (optional)
    }

    output:
        optionsDict = {
            item1: amount
            item2: amount,
            ...
        }
    """
    resolvedOption = []
    if len(optionsList) < 2:
        option = optionsList
        logger.warning("At least on meal has only one choice in the option field")
    else:
        option = getRandomOption(optionsList)
    for optionIngredient in option:
        optionIngredientObject = getIngredientObject(IngredientObjectList, optionIngredient)
        if optionIngredientObject:
            optionIngredientObject.amount = option[optionIngredient]
            resolvedOption.append(optionIngredientObject)
        else:
            resolvedOption = []
            break
    return resolvedOption

def tagWorkoutMeals(postWorkoutMealDict, preWorkoutMealDict):
    """
    """
    for postWorkoutMeal in postWorkoutMealDict:
        postWorkoutMealDict[postWorkoutMeal]["postWorkout"] = True
    for preWorkoutMeal in preWorkoutMealDict:
        preWorkoutMealDict[preWorkoutMeal]["preWorkout"] = True
    return postWorkoutMealDict, preWorkoutMealDict

def separateMeals(mealList):
    """
    Separates the given mealList in pre workout, post workout and regular meals.
    """
    postWorkoutMealList = []
    preWorkoutMealList = []
    regularMealList = [] 

    for meal in mealList:
        if meal.postWorkout:
            postWorkoutMealList.append(meal)
        elif meal.preWorkout:
            preWorkoutMealList.append(meal)
        else:
            regularMealList.append(meal)
            
    return postWorkoutMealList, preWorkoutMealList, regularMealList

def getRandomOption(options):
    return random.choice(options)

def improveChoosenMealList(mealList, choosenMealList):
    return choosenMealList
