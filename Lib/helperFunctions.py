import logging
import sys

from pathlib import Path

from ingredient import registerIngredientLogger
from meal import registerMealLogger


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