import logging

logger = logging.getLogger(__name__) 

def registerIngredientLogger(Logger):
    global logger
    logger = Logger

# class Ingredient --------------------------------------------------------------------------------------
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
    def __init__(self, name, kcal, carb, protein, fat, metric, amount = 0):
        self.name = name
        self.kcal = kcal
        self.carb = carb
        self.protein = protein
        self.fat = fat
        self.metric = metric
        self.amount = amount

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
        ingredientDescriptionString += " metric: " + str(self.metric) + "> \n\n"
        return ingredientDescriptionString
