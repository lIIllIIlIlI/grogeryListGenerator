import yaml


macros = [ 
            {  'name': 'Tomate',
               'kcal': 100,
               'Fat': 0,
               'Protein': 2,
               'Carbs': 10,    
            },
            { 
               'name': 'Mozarella',
               'kcal': 100,
               'Fat': 0,
               'Protein': 2,
               'Carbs': 10,    
            },
        ]

meals = [
            {
            'name': 'Frittn',
            'incredience': 
                {
                    'kartoffeln': 400,
                    'Bratfett': 20,
                    'Thymian': 2,
                },
            },
            {
            'name': 'Frittn2',
            'incredience': 
                {
                    'kartoffeln': 400,
                    'Bratfett': 20,
                    'Thymian': 2,
                    'Option': 
                    [
                        {
                            'krauter': 40,
                        },
                        {
                            'Butter': 20,
                            'Lauch': 10,
                        },
                    ],                    
                },
            },

        ]

with open('test.yaml', 'w') as yamldump:
    yaml.dump(meals, yamldump)