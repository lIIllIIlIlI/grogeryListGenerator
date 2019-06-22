###################################################################################################
#                                Description                                                      #
#    Creates a grogery list from given meals and ingredience that will fit for given number of    #
#    days.                                                                                         #
#                                                                                                 #
#    Author: Lukas                                                                                #
#                                                                                                 #
#    Contact: -                                                                                   #   
#                                                                                                 #
###################################################################################################


###################################################################################################
#                                Imports                                                          #
###################################################################################################
import logging
import sys
import argparse

from pathlib import Path


###################################################################################################
#                                Input Arguments                                                  #
###################################################################################################
parser = argparse.ArgumentParser()

# define input options
parser.add_argument('--days', '-d', help = 'Number of days the grogerys should last', type = int, required = True)
parser.add_argument('--nocarb','-n', help = 'Make the generator filter out high carb meals', action="store_true", default=False)
parser.add_argument('--workout', '-w', help='Number of workouts during the choosen period of time', type = int, default = False)
parser.add_argument('--cheatmeals', '-c', help='Number of meals that are taken outside during the choosen period', type = int, default = False)
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
        
    
    
    
    
if __name__ == '__main__':
    init()

