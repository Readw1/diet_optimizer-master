ACTIVITY_LEVEL_CHOICES = (
    ('Sedentary', ("Sedentary")),
    ('Low Active', ("Low Active")),
    ('Active', ("Active")), 
    ('Very Active', ("Very Active"))
)

DIET_CHOICES = (
    ('None', ('None')), 
    ('pescetarian', ('Pescetarian')),
    ('Lacto Vegetarian', ('Lacto Vegetarian')),
    ('Ovo Vegetarian', ('Ovo Vegetarian')),
    ('Vegan', ('Vegan')), 
    ('Paleo', ('Paleo')),
    ('Primal', ('Primal')), 
    ('Vegetarian', ('Vegetarian'))
)

GENDER_CHOICES = (
    ('Male', ('Male')), 
    ('Female', ('Female'))
)

INTOLERENCES_CHOICES = (
    ('None',('None')), 
    ('Dairy', ('Dairy')), 
    ('Egg', ('Egg')),
    ('Gluten', ('Gluten')), 
    ('Peanut', ('Peanut')), 
    ('Sesame', ('Sesame')),
    ('Seafood', ('Seafood')), 
    ('Shellfish', ('Shellfish')), 
    ('Soy', ('Soy')),
    ('Sulfite', ('Sulfite')), 
    ('Tree Nut', ('Tree Nut')), 
    ('Wheat', ('Wheat'))
)

CUISINES_CHOICES = (
    ('African',('African')), 
    ('American', ('American')), 
    ('British', ('British')),
    ('Cajun', ('Cajun')), 
    ('Caribbean', ('Caribbean')), 
    ('Chinese', ('Chinese')),
    ('Eastern European', ('Eastern European')), 
    ('French', ('French')), 
    ('German', ('German')),
    ('Greek', ('Greek')), 
    ('Indian', ('Indian')), 
    ('Irish', ('Irish')),
    ('Italian', ('Italian')),
    ('Japanese', ('Japanese')),
    ('Jewish', ('Jewish')),
    ('Korean', ('Korean')),
    ('Latin American', ('Latin American')),
    ('Mexican', ('Mexican')),
    ('Middle Eastern', ('Middle Eastern')),
    ('Nordic', ('Nordic')),
    ('Southern', ('Southern')),
    ('Spanish', ('Spanish')),
    ('Thai', ('Thai')),
    ('Vietnamese', ('Vietnamese'))
)


RECIPE_TYPES_CHOICES = (
    ('Main Course',('Main Course')), 
    ('Side Dish', ('Side Dish')), 
    ('Dessert', ('Dessert')),
    ('Appetizer', ('Appetizer')), 
    ('Salad', ('Salad')), 
    ('Bread', ('Bread')),
    ('Breakfast', ('Breakfast')), 
    ('Soup', ('Soup')), 
    ('Beverage', ('Beverage'))
)


RAW_GROUPS_CHOICES = (
    ('American Indian/Alaska Native Foods',('American Indian/Alaska Native Foods')), 
    ('Baby Foods', ('Baby Foods')), 
    ('Baked Products', ('Baked Products')),
    ('Beef Products', ('Beef Products')), 
    ('Beverages', ('Beverages')), 
    ('Breakfast Cereals', ('Breakfast Cereals')),
    ('Cereal Grains and Pasta', ('Cereal Grains and Pasta')), 
    ('Dairy and Egg Products', ('Dairy and Egg Products')), 
    ('Fast Foods', ('Fast Foods')),
    ('Fats and Oils', ('Fats and Oils')), 
    ('Finfish and Shellfish Products', ('Finfish and Shellfish Products')), 
    ('Fruits and Fruit Juices', ('Fruits and Fruit Juices')),
    ('Lamb, Veal, and Game Products', ('Lamb, Veal, and Game Products')),
    ('Legumes and Legume Products', ('Legumes and Legume Products')),
    ('Meals, Entrees, and Side Dishes', ('Meals, Entrees, and Side Dishes')),
    ('Nut and Seed Products', ('Nut and Seed Products')),
    ('Pork Products', ('Pork Products')),
    ('Poultry Products', ('Poultry Products')),
    ('Restaurant Foods', ('Restaurant Foods')),
    ('Sausages and Luncheon Meats', ('Sausages and Luncheon Meats')),
    ('Snacks', ('Snacks')),
    ('Soups, Sauces, and Gravies', ('Soups, Sauces, and Gravies')),
    ('Spices and Herbs', ('Spices and Herbs')),
    ('Sweets', ('Sweets')),
    ('Vegetables and Vegetable Products', ('Vegetables and Vegetable Products'))
)

OBJECTIVES_CHOICES =(
    ('Calories',('Calories')),
    ('Protein',('Protein')),
    ('Carbs',('Carbs')),
    ('Fat',('Fat')),
    ('Price',('Price'))
)

MIN_MAX_CHOICES = (
    ('Min', ('Min')),
    ('Max', ('Max'))
)