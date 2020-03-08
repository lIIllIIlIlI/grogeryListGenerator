from Class.ingredient import ingredient

import logging

logger = logging.getLogger(__name__) 

def registerMealLogger(Logger):
    global logger
    logger = Logger

# class meal --------------------------------------------------------------------------------------
#
#   Meal object represents meal recipe with its nutrition
#   
#       watchList - list of additives to keep in stock for the meal 
#   
#       ingredientList - list of fully resolved ingredients
#               [
#                   ingredient1,
#                   ingredient2,
#                   ...
#               ]
#
#       options - several mutually exclusive meal variant options  
#               [[ingredient1, ingredient2, ..], [ingrdient 1, ...]]
#
#       kcal - overall kcal count of the meal
#
#       carb - overall carb count of the meal
#
#       protein - overall protein count of the meal
#
#       fat - overall fat count of the meal
#
#       postWorkout - indicator for meals that are only suitable for post workout
#
#       preWorkout - indicator for meals that are only suitable for pre workout
#
# -------------------------------------------------------------------------------------------------

class meal:
    def __init__(self, name, watchList, postWorkout, preWorkout, ingredientList = []):
        self.name = name
        self.watchList = watchList
        self.ingredientList = ingredientList
        self.postWorkout = postWorkout
        self.preWorkout = preWorkout
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
        mealDescriptionString += " ingredients: " + str(", ".join([ingredient.name for ingredient in self.ingredientList])) + ",\n"
        mealDescriptionString += " watchList: " + str(self.watchList) + ",\n"
        mealDescriptionString += " macros (K|C|P|F): " + str(self.kcal) + " " + \
                                   str(self.carb) + " " + str(self.protein) + " " + \
                                   str(self.fat) + ",\n"
        mealDescriptionString += " watchList: " + str(self.watchList) + ",\n"
        mealDescriptionString += " >\n"
        return mealDescriptionString

    def resolveMacros(self):
        for ingredient in self.ingredientList:
            # if more than 10 units of the ingredient are requested, its assumed to
            # be "gram". Else, itt assumed to be number of elements. 
            if ingredient.amount > 10:
                self.kcal += ingredient.kcal * ingredient.amount / 100
                self.carb += ingredient.carb * ingredient.amount / 100
                self.protein += ingredient.protein * ingredient.amount / 100
                self.fat += ingredient.fat * ingredient.fat / 100

            else:
                self.kcal += ingredient.kcal * ingredient.amount 
                self.carb += ingredient.carb * ingredient.amount 
                self.protein += ingredient.protein * ingredient.amount
                self.fat += ingredient.fat * ingredient.fat
        return
    
    