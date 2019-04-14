from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User
from django.conf import settings
from pulp import *
from .choices import *
import json
import datetime
import timeit
import random
import requests
import re


# Create your models here.
class UserDB(models.Model):
    """Class representing an user. In this class will be stored all data about 
    an user.

    :param user: This attribut is a One to One Field link to the django class 
        User. In the class User are stored the first name, last name, username,
        email and pasword of an user.
    :param height: The user's height.
    :param weight: The user's weight.
    :param birth_date: The user's birth date.
    :param activity_level: The user's activity level. It's a CharField and the 
        user must choose between Sedentary, Low Active, Active, Very Active.
    :param diet: The user's diet. It's a CharField and the user must choose 
        between a list of diet like Paleo, Vega, etc... If the user has any diet, 
        he can chose None.
    :param gender: the user's gender. It's a CharField and the 
        user must choose between Male or Female.
    :param accepts_popups: This is a boolean. It's set to true if the user 
        accepts to have a warning if during his recipe's search he puts food 
        prohibited by his diet or intolerences. The user can deactivate this pop up
        thus the attribut would be set to false.
    :param timeToCook: The user can set, in his preferences, the maximum time
        he usually have to cook. During a recipe's search, the total time of 
        suggested recipes wont exceed this time (if he doesn't change it in the
        get recipe's form).

    .. note:: There is no intolerence attribut in this class. Indeed, there is
        an Intolerence class, which is link to the user's data with a ForeignKey
        attribut userdb. Thus the UserDB class is link to the user's intolerences 
        thanks to the userdb attribut of the Intolerence class.
    """
    # The user_id of the User class object will be stock in the fiel "user"
    # of UserDB. The field "user" of UserDB is named "user_id" in the DB.
    user = models.OneToOneField(
        User,
        on_delete = models.CASCADE,
        primary_key=True)
    # The 5 following fields are already handled by User class in django
    # first_name, last_name, email, password, username (=nickname here).
    # firstname = models.CharField(max_length=100, default=" ")
    # lastname = models.CharField(max_length=300, default=" ")
    # nickname = models.CharField(max_length=100,  unique = True, default=" ")
    # email = models.CharField(max_length=120,  unique = True, default=" ")
    # pwdhash = models.CharField(max_length=100, default=" ")

    height = models.PositiveSmallIntegerField(default=0)
    weight = models.PositiveSmallIntegerField(default=0)
    birth_date = models.DateField(
        auto_now=False,
        auto_now_add=False,
        null=True,
        blank=True,
        default=None,
        help_text="Required. Format: MM-DD-YYYY")
    activity_level = models.CharField(
        choices=ACTIVITY_LEVEL_CHOICES,
        max_length=100,
        null=True,
        blank=True,
        default='Sedentary')
    diet = models.CharField(
        choices=DIET_CHOICES,
        max_length=100,
        null=True,
        blank=True,
        default=None)
    gender = models.CharField(
        choices=GENDER_CHOICES,
        max_length=100,
        null=True,
        blank=True,
        default=None)
    #intolerences = models.Column(models.String(15))
    accepts_popups = models.BooleanField(default=True)
    timeToCook = models.PositiveSmallIntegerField(default=30)

    class Meta:
        db_table = 'users'

    def user_as_dict(self):
        """
        This function cast an User object (attribut of an UserDB object) into a 
        dictionnary. This is usefull when we need to send an UserDB or an User in 
        a request.

        :returns: The dictionnary representing the User. 
        """
        context = {
            'username': self.user.username,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'email': self.user.email,
            'password': self.user.password
        }

    def as_dict(self):  
        """
        This function cast an UserDB object into a dictionnary. This is usefull
        when we need to send an UserDB in a request.

        :returns: The dictionnary representing the UserDB.
        """
        context = {
            'user':self.user_as_dict(),
            'height': self.height,
            'weight': self.weight,
            #Birth date is not useful for what we do there
            #'birth_date': self.birth_date,
            'activity_level': self.activity_level,
            'diet': self.diet,
            'gender': self.gender
        }
        return context


class Recipe(models.Model):
    """Class representing a Recipe. In this class will be stored some data 
    about a Recipe.

    :param recipe_id_api: Recipes are referenced in spoonacular with a
        different id than the one automatically generate by django. recipes_id_api
        attribut is the recipe's id of spoonacular.
    :param title: The title's recipe.
    :param link: The spoonacular link's recipe.
    :param likes: The number of likes that the recipe has.
    :param dislikes_no_opinion: The addition of dislikes and no opinion that 
        the recipe has.
    :param percent: The percentage of likes out of all votes (likes + dislikes
        + no opinion) for the recipe.

    .. note:: All recipes used are in Spoonacular. The diet optimizer website
        access these recipes and stores the data of previous fields in the Recipe's
        table. 
    """
    # Django automatically will add an id field for this class.
    # To get it, use recipe.pk on an Recipe object here named "recipe".
    recipe_id_api = models.IntegerField(default=0)
    title = models.CharField(max_length=100, default=None)
    link = models.CharField(max_length=1000, default=None)
    likes = models.PositiveIntegerField(default=0)
    dislikes_no_opinion = models.PositiveIntegerField(default=0)
    percent = models.FloatField(default=0)

    # Unused function. Uncomment if you ever need this.
    # def as_dict(self):
    #     """
    #     This function cast a Recipe object into a dictionnary. This is
    #     usefull when we need to send a Recipe in a request.
    #     """
    #     context = {                      
    #         'recipe_id_api': self.recipe_id_api,
    #         'title': self.title,
    #         'link': self.link
    #     }
    #     return context

    class Meta:
        db_table = 'recipes'
        ordering = ['-percent', '-likes']


class Saved_Recipes(models.Model):
    """Class representing a Recipe. In this class will be stored some data 
    about a Recipe.

    :param user: The user who saved the recipes. This is a ForeignKey
        relation, thus this is a user object.
    :param diet_recipes: All data from spoonacular used for displaying 
        information about a group of recipes saved by the user.
    :param total_nutrients_taken: The total nutrients that a group of recipes
        provides.
    """
    # Django automatically will add an id field for this class.
    user = models.ForeignKey(
        'UserDB',
        on_delete=models.CASCADE,
        default=1)
    diet_recipes = models.TextField(max_length=1000000, default=None)
    total_nutrients_taken = models.CharField(max_length=2000, default=None)

    class Meta:
        db_table = "saved_recipes"


class Feedback(models.Model):
    """Class representing a Feedback from an user for a recipe.

    :param recipe: The recipe concerned by the feedback. This is a ForeignKey
        relation, thus this is a Recipe object.
    :param user:  The user whose the feedback it is. This is a ForeignKey
        relation, thus this is an UserDB object.
    :param mark: The mark that the user gave for the recipe's feedback. 
        mark = 1 means that the user liked it, 
        mark = 2 means that the user disliked it, 
        mark = 3 means that the user has no opinion, 
        mark = 4 means that the user didn't try it yet.
    :param title: The feedback's title. It's equal to the recipe's title that 
        is linked to the feedback, so the feedback's title is not unique.
    """
    # Django automatically will add an id field for this class.
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        default=1)
    user = models.ForeignKey(
        'UserDB',
        on_delete=models.CASCADE,
        default=1)
    mark = models.PositiveSmallIntegerField(default=4)
    #the title of feedback is equal to the recipe title, so it's not unique.
    # If you want to change this, go to the results view
    title = models.CharField(max_length=200,
        default=None,
        null = True,
        blank = True)

    # Unused function. Uncomment if you ever need this.
    # def as_dict(self):
    #     """
    #     This function cast a Feedback object into a dictionnary. This is
    #     usefull when we need to send a Feedback in a request.
    #     """
    #     context = {
    #         'recipe': self.recipe.as_dict(),
    #         'user': self.user.as_dict(),
    #         'mark': self.mark
    #     }
    #     return context

    class Meta:
        ordering = ['mark', 'title']
        db_table = 'feedback'


class Intolerences(models.Model):
    """Class representing Introlerence(s) of users.

    :param userdb:  The user whose the cuisines intolerence it is. This is a ForeignKey
        relation, thus this is an UserDB object.
    :param intolerence_name: The name of the intolerence that the user has.

    .. note:: There is a row per user and per intelorence. For instance if a user
        has 2 intolerences, there'll be 2 rows in the db, with the reference to 
        the user and the name of each intolerence.
    """
    # Django automatically will add an id field for this class.
    # To get it, use intolerences.pk on an Intolerences object here
    #  named "intolerences".
    userdb = models.ForeignKey(
        'UserDB',
        on_delete=models.CASCADE,
        default=1) #PrimaryKey?
    intolerence_name = models.CharField(
        max_length=100,
        default=" ")

    class Meta:
        db_table = 'intolerences'


class PreferenceCuisines(models.Model):
    """Class representing the cuisines the user prefer.

    :param userdb: The user whose the cuisines preference it is. This is a ForeignKey
        relation, thus this is an UserDB object.
    :param cuisine_name: The name of the preference that the user has.

    .. note:: This class is used to store the cuisines preference in order
        to pre fill the form when the user wants to get recipes. The user can 
        change his preferences in the diet settings page.
        There is a row per user and per cuisines preference. For instance if a user
        has 2 cuisines preference, there'll be 2 rows in the db, with the reference 
        to the user and the name of each cuisines preference.
    """
    userdb = models.ForeignKey(
        'UserDB',
        on_delete=models.CASCADE,
        default=1)
    cuisine_name = models.CharField(
        max_length=100,
        default=" ")

    class Meta:
        db_table = 'preference_cuisines'


class PreferenceRawFoods(models.Model):
    """Class representing the raw food the user prefer.

    :param userdb: The user whose the raw food preference it is. This is a ForeignKey
        relation, thus this is an UserDB object.
    :param cuisine_name: The name of the preference that the user has.

    .. note:: This class is used to store the raw food preferences in order
        to pre fill the form when the user wants to get recipes. The user can 
        change his preferences in the diet settings page.
        There is a row per user and per raw food preference. For instance if a user
        has 2 raw food preferences, there'll be 2 rows in the db, with the reference 
        to the user and the name of each raw food preference.
    """
    userdb = models.ForeignKey(
        'UserDB',
        on_delete=models.CASCADE,
        default=1)
    raw_food_name = models.CharField(
        max_length=100,
        default=" ")

    class Meta:
        db_table = 'preference_raw_food'


# Ryan added code
# More info on : https://ndb.nal.usda.gov/ndb/doc/apilist/API-FOOD-REPORT.md ?
class USDAfoods(models.Model):
    """Class representing the different raw foods.

    :param NDB_No: Automatic ID representing the number of the food in the database.
    :param desc: Description of the food.
    :param calorie: The number of calories a portion of this food provides.
    :param protein: The number of protein a portion of this food provides (in g).
    :param fat: The number of fat a portion of this food provides (in g).
    :param carb: The number of carbohydrates a portion of this food provides (in g).
    :param group_code: The code number of the group this food belongs to.
    :param group_name: The name of the group this food belongs to.

    .. note:: Below are other fields used to enable food popularity.

        :param likes: The number of likes this food got.
        :param dislikes_no_opinion: the number of dislikes or no opinion that
            this food got.
        :param percent: The percentage of likes this food got comparend to the
            total number of votes it got.
    """
    NDB_No = models.IntegerField(primary_key = True, default=1)
    # use the automatic id of django instead of NDB_No
    desc = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        default=None)
    calorie =  models.IntegerField(default=None)
    protein =  models.IntegerField(default=None)
    fat =  models.IntegerField(default=None)
    carb =  models.IntegerField(default=None)
    group_code =  models.IntegerField(default=None)
    group_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None)
    # Uncomment if you want to enable food popularity
    # likes = models.PositiveIntegerField(default=0)
    # dislikes_no_opinion = models.PositiveIntegerField(default=0)
    # percent = models.FloatField(default=0)

    class Meta:
        # ordering = ['-percent', '-likes']
        db_table = 'usda'

    # Unused function. Uncomment if you ever need this.
    # def as_dict(self):
    #     """
    #     This function cast an USDAfood object into a dictionnary. This is
    #     usefull when we need to send an USDAfood in a request.
    #     """
    #     context = {
    #         'NDB_No': self.NDB_No,
    #         'desc': self.desc,
    #         'calorie': self.calorie,
    #         'protein': self.protein,
    #         'fat': self.fat,
    #         'carb': self.carb,
    #         'group_code': self.group_code,
    #         'group_name': self.group_name
    #     }
    #     return context


class FeedbackRawFood(models.Model):
    """Class representing a Feedback from an user for a raw food.

    :param food: The raw food concerned by the feedback. This is a ForeignKey
        relation, thus this is a USDAfoods object.
    :param user:  The user whose feedback it is. This is a ForeignKey
        relation, thus this is an UserDB object.
    :param mark: The mark that the user gave for the raw food's feedback. 
        mark = 1 means that the user liked it, 
        mark = 2 means that the user disliked it, 
        mark = 3 means that the user has no opinion, 
        mark = 4 means that the user didn't try it yet.
    :param title: The feedback's title. It's equal to the raw food's title that 
        is linked to the feedback, so the feedback's title is not unique.
    """
    # Django automatically will add an id field for this class.
    food = models.ForeignKey(
        'USDAfoods',
        on_delete=models.CASCADE,
        default=1)
    user = models.ForeignKey(
        'UserDB',
        on_delete=models.CASCADE,
        default=1)
    mark = models.PositiveSmallIntegerField(default=4)
    #the title of feedback raw food is equal to the food desc, so it is not
    #unique. If you want to change this, go to the results view
    title = models.CharField(
        max_length=200,
        default=None,
        null = True,
        blank = True)

    # Unused function. Uncomment if you ever need this.
    # def as_dict(self):
    #     """
    #     This function cast a FeedbackRawFood object into a dictionnary. This
    #     is usefull when we need to send a FeedbackRawFood in a request.
    #     """
    #     context = {
    #         'food': self.food.as_dict(),
    #         'user': self.user.as_dict(),
    #         'mark': self.mark
    #     }
    #     return context

    class Meta:
        ordering = ['mark', 'title']
        db_table = 'feedbackrawfood'


class UserData():
    """This class represents various data about the user that he didn't enter himself.

    For that it will use the information it knows about the user to calculate new data.
    This class has 6 fields:

    :param age: The age of the user, calculated thanks to his birth date.
    :param gender: The user's gender.
    :param weight: The user's weight.
    :param height: The user's height.
    :param exercise_level: The user's exercise level.
    :param daily_nutrients: A dictionnary containing the amount of nutrients the user
        should consume daily in general.
    """
    def __init__(self, user):
        """This function will initialize the UserData object.

        :param user: The user who's data we want to calculate.

        :returns: The UserData object we want to create.
        """
        # age calculation:
        def get_age(userDB):
            """This function will use the user's birth date to calculate his age and return it.

            :param userDB: The user who's birth date we will use.

            :returns: An integer, the age of the user.

            """
            if userDB.birth_date > datetime.date.today().replace(year = userDB.birth_date.year):
                return datetime.date.today().year - userDB.birth_date.year - 1
            else:
                return datetime.date.today().year - userDB.birth_date.year

        userDB = user.userdb
        self.age = get_age(userDB)
        self.gender = userDB.gender
        self.weight = userDB.weight
        self.height = userDB.height
        self.exercise_level = userDB.activity_level
        self.daily_nutrients = self.get_daily_nutrients()

    def get_BMI(self):
        """This function calculate's the BMI of the user.

        :returns: A float, the user's BMI.
        """
        # calculating user's BMI.
        return round(self.weight/(self.height*self.height*0.0001),2)

    def get_daily_nutrients(self):
        """This function calculates the minimum and maximum amount of each nutrients the
        user should take daily.
        
        :returns: A dictionnary, containing all these nutrient information in addition to the user's BMI.
        """
        # calculates daily nutrients needed for the user.
        daily_nutrients = {}
        calories = self.get_calorie()
        daily_nutrients["cal_low"] = round(calories * 0.9, 1)
        daily_nutrients["cal_up"] = round(calories * 1.1, 1)
        bmi = self.get_BMI()
        daily_nutrients["bmi"] = bmi
        carb_low = self.get_carb_lower(calories)
        daily_nutrients["carb_low"] = carb_low
        carb_up = self.get_carb_upper(calories)
        daily_nutrients["carb_up"] = carb_up
        prot_low = self.get_protein_lower(calories)
        daily_nutrients["prot_low"] = prot_low
        prot_up = self.get_protein_upper(calories)
        daily_nutrients["prot_up"] = prot_up
        fat_low = self.get_fat_lower(calories)
        daily_nutrients["fat_low"] = fat_low
        fat_up = self.get_fat_upper(calories)
        daily_nutrients["fat_up"] = fat_up
        return  daily_nutrients

    def get_PA(self):
        """This function will calculate a number representing the user's
        physical activity.

        :returns: An arbitrary float representing the user's physical activity.
        """
        # arbitrary scale of numbers to represent user's physical activity.
        if self.exercise_level == 'Sedentary':
            return 1.00
        if self.exercise_level == 'Low Active':
            if (self.gender == 'Male' and self.age < 19):
                return 1.13
            if (self.gender == 'Female' and self.age < 19):
                return 1.16
            if (self.gender == 'Male' and self.age >= 19):
                return 1.11
            if (self.gender == 'Female' and self.age >= 19):
                return 1.12
        if self.exercise_level == 'Active':
            if (self.gender == 'Male' and self.age < 19):
                return 1.26
            if (self.gender == 'Female' and self.age < 19):
                return 1.31
            if (self.gender == 'Male' and self.age >= 19):
                return 1.25
            if (self.gender == 'Female' and self.age >= 19):
                return 1.27
        if self.exercise_level == 'Very Active':
            if (self.gender == 'Male' and self.age < 19):
                return 1.42
            if (self.gender == 'Female' and self.age < 19):
                return 1.56
            if (self.gender == 'Male' and self.age >= 19):
                return 1.48
            if (self.gender == 'Female' and self.age >= 19):
                return 1.45

    ##Calories
    ##ages younger than 3 years and pregnancy situations are not considered.
    def get_calorie(self):
        """This function will calculate the user's physical activity and
        calculate accordingly the number of calories the user should take daily,
        also considering his age and gender.

        :returns: A float, representing the number of calories the user should take daily.
        """
        ##height was divided by 100 because of cm m conversion.
        pa = self.get_PA()
        if (self.gender == 'Male' and self.age < 9):
            eer = (88.5-(61.9*self.age)+pa*((26.7*self.weight)+(903*self.height/100)))+20
        if (self.gender == 'Male' and 9 <= self.age < 19):
            eer = (88.5-(61.9*self.age)+pa*((26.7*self.weight)+(903*self.height/100)))+25

        if (self.gender == 'Female' and self.age < 9):
            eer = (135.3-(30.8*self.age)+pa*((10*self.weight)+(934*self.height/100)))+20
        if (self.gender == 'Female' and 9 <= self.age < 19):
            eer = (135.3-(30.8*self.age)+pa*((10*self.weight)+(934*self.height/100)))+25

        if (self.gender == 'Male' and self.age >= 19):
            eer = (662-(9.53*self.age)+pa*((15.91*self.weight)+(539.6*self.height/100)))
        if (self.gender == 'Female' and self.age >= 19):
            eer = (354-(6.91*self.age)+pa*((9.36*self.weight)+(726*self.height/100)))
        return round(eer)

    ##Carbs
    def get_carb_lower(self, calories):
        """This function calculates the minimum amount of carbohydrates the
        user should consume per day.

        :param calories: The amount of calories the user should take daily.

        :returns: A float, minimum number of carbs the user should have per day.
        """
        x = 4 #energy provided by carbs/g
        return round(0.45*calories/x)

    def get_carb_upper(self, calories):
        """This function calculates the maximum amount of carbohydrates the
        user should consume per day.

        :param calories: The amount of calories the user should take daily.

        :returns: A float, maximum number of carbs the user should have per day.
        """
        x = 4 #energy provided by carbs/g
        return round(0.65*calories/x)

    ##Protein
    def get_protein_lower(self, calories):
        """This function calculates the minimum amount of proteins the
        user should consume per day.

        :param calories: The amount of calories the user should take daily.

        :returns: A float, minimum number of proteins the user should have per day.
        """
        x = 4 #energy provided by protein/g
        if self.age < 4:
            return round(0.05*calories/x)
        if self.age < 19:
            return round(0.1*calories/x)
        return round(0.1*calories/x)

    def get_protein_upper(self, calories):
        """This function calculates the maximum amount of proteins the
        user should consume per day.

        :param calories: The amount of calories the user should take daily.

        :returns: A float, maximum number of proteins the user should have per day.
        """
        x = 4 #energy provided by protein/g
        if self.age < 4:
            return round(0.2*calories/x)
        if self.age < 19:
            return round(0.3*calories/x)
        return round(0.35*calories/x)

    ##Fat
    def get_fat_lower(self, calories):
        """This function calculates the minimum amount of fat the
        user should consume per day.

        :param calories: The amount of calories the user should take daily.

        :returns: A float, minimum number of fat the user should have per day.
        """
        x = 9 #energy provided by fat/g
        if self.age < 4:
            return round(0.3*calories/x)
        if self.age < 19:
            return round(0.25*calories/x)
        return round(0.2*calories/x)

    def get_fat_upper(self, calories):
        """This function calculates the maximum amount of fat the
        user should consume per day.

        :param calories: The amount of calories the user should take daily.

        :returns: A float, maximum number of fat the user should have per day.
        """
        x = 9 #energy provided by fat/g
        if self.age < 4:
            return round(0.4*calories/x)
        if self.age < 19:
            return round(0.35*calories/x)
        return round(0.35*calories/x)


class RecipeHandler(object):
    """The RecipeHandler class is the one making sure the user will only be provided recipes that match what he is searching for.
    """

    def __init__(self, userDB, user_daily_nutrients, cuisine, diet, intolerances, exclude_ingredients, recipe_types):
        """This function creates the RecipeHandler object.

        :param userDB: The user asking for recipes.
        :param user_daily_nutrients: The amount of nutrients the user asked for.
        :param cuisine: The type of cuisine the user asked for.
        :param diet: The user's diet.
        :param intolerances: The user's intolerances.
        :param exclude_ingredients: List of ingredients that should not be in the recipes.
        :param recipe_types: The types of recipes that the user asked for.

        :returns: The RecipeHandler object we wanted to create.
        """
        self.userDB = userDB
        self.user_daily_nutrients = user_daily_nutrients
        self.recipe_types = recipe_types
        self.cuisine = cuisine
        self.diet = diet
        self.intolerances = intolerances
        self.exclude_ingredients = exclude_ingredients

    def get_URL(self, recipe_type, offset):
        """Function used to get the url for spoonacular.

        :param recipe_type: The type of recipe we want our url to find.
        
        :returns: A string. The URL that will be sent to spoonacular.

        .. note:: offset is also a parameter but we have no idea what it stands for. It is just part of the URL for spoonacular.
        """
        add_recipe_info = "true"
        fill_ingredients = "false"
        limit_license = "false"
        number = "100"
        query = "recipe"
        ranking = "1"

        # starting to create the url as a string.
        req_URL = "https://spoonacular-recipe-food-nutrition-v1.p.mashape.com/recipes/searchComplex?addRecipeInformation=" + add_recipe_info

        if self.cuisine != None:
            # adding the cuisines to a string.
            cuisine_str = ",".join(self.cuisine)
            # replacing spaces with "+" and "," with "%2C" for encoding reasons.
            cuisine_str = cuisine_str.replace(" ", "+")
            cuisine_str = cuisine_str.replace(",", "%2C")
            # adding the string to the url.
            req_URL += "&cuisine=" + cuisine_str

        if self.diet != None:
            # adding the diet to a string.
            diet_str = self.diet
            # replacing spaces with "+" for encoding reasons.
            diet_str = diet_str.replace(" ", "+")
            # adding the string to the url.
            req_URL += "&diet=" + diet_str

        # adding the information about filling ingredients in the url.
        req_URL += "&fillIngredients=" + fill_ingredients

        # if the user has intolerences
        if self.intolerances != None:
            # adding the list of intolerences in a string.
            intolerances_str = ",".join(self.intolerances)
            # replacing spaces with "+" and "," with "%2C" for encoding reasons.
            intolerances_str = intolerances_str.replace(" ", "+")
            intolerances_str = intolerances_str.replace(",", "%2C")
            # adding the string to the url. 
            req_URL += "&intolerances=" + intolerances_str

        # adding the information about nutrients in the url.
        req_URL +=  "&limitLicense=" + limit_license + "&maxCalories="+ str(self.user_daily_nutrients['cal_up']) + "&maxCarbs=" + str(self.user_daily_nutrients['carb_up']) + "&maxFat=" + str(self.user_daily_nutrients['fat_up']) + "&maxProtein=" + str(self.user_daily_nutrients['prot_up']) + "&minCalories=" + str(0) + "&minCarbs=" + str(0) + "&minFat=" + str(0) + "&minProtein=" + str(0)

        # adding other various information into the url.
        req_URL += "&number=" + number + "&offset=" + str(offset) + "&query=" + query + "&ranking=" + ranking

        # if the user asked for peculiar recipes types.
        if recipe_type != None:
            # replacing spaces with "+" and "," with "%2C" for encoding reasons.
            recipe_type = str(recipe_type).replace(" ", "+")
            recipe_type = str(recipe_type).replace(",", "%2C")
            # adding the string to the url.
            req_URL += "&type=" + recipe_type

        return req_URL

    def get_recipes(self): # The issues happen here.
        """ Function used to get the list of the recipes usable with the user's request.

        :returns: A dictionnary filled with other dictionnarys containing various information 
            about the recipes foud that satisfy the user's needs.
        """
        unique_IDs = []
        dict_keys = []
        dict_title = {}
        dict_cal = {}
        dict_prot = {}
        dict_carb = {}
        dict_fat = {}
        dict_price = {}
        dict_time = {}

        strings_timer = []

        # getting the feedbacks of all the recipes the user didn't like.
        not_liked_recipes_feedbacks = Feedback.objects.filter(user=self.userDB,mark=3)
        not_liked_recipes_ids = []
        for feedback in not_liked_recipes_feedbacks:
            not_liked_recipes_ids.append(feedback.recipe.recipe_id_api)

        # for every type of recipes the user asked for:
        for recipe_type_index in range(len(self.recipe_types)):

            outer_start = timeit.default_timer()

            offset = random.randrange(0, 500)
            reached_length = False
            counter = 0
            while not reached_length and counter < 2:

                inner_start = timeit.default_timer()

                for i in range(1,2):

                    part1_start = timeit.default_timer()

                    offset = i*offset #if range is bigger than one, you can get more results (one api call returns 100 recipes)
                    # getting the url we'll load to have the response.
                    req_URL = self.get_URL(self.recipe_types[recipe_type_index], offset)
                    # preparing headers necessary for spoonacular API.
                    headers = {"X-Mashape-Key": settings.SPOONACULAR_KEY,
                                "Accept": "application/json"}
                    # requesting the URL.
                    response = requests.get(req_URL,
                                            headers = headers,
                                            timeout=100)

                    # loading the reponse data into a json format.
                    json_data_load = json.loads(response.text)
                    json_data = json_data_load.get("results")

                    if len(json_data) < 30:
                        offset = random.randrange(0, 500)
                        counter += 1

                    else:
                        reached_length = True
                        counter = 4

                    val_title = []
                    val_prot = []
                    val_carb = []
                    val_cal = []
                    val_fat = []
                    val_price = []
                    val_time = []

                    # calculating time for response
                    part1_total = timeit.default_timer() - part1_start
                    s = 'Part 1 time: %f' % (part1_total)
                    strings_timer.append(s)
                    part2_start = timeit.default_timer()

                    # for every recipe given in the json data:
                    for d in json_data:
                        # if the recipe has not already been given in a previous load:
                        if d["id"] not in unique_IDs:
                            k = d['id']
                            # if the recipe has not already been unliked by the user
                            if k not in not_liked_recipes_ids:
                                # add the recipe ID to the usable IDs for the optimization problem.
                                unique_IDs.append(k)
                                dict_keys.append(k)
                            else:
                                print("user didn't like this recipe")
                            for key, value in d.items():
                                # gathering all the info about the recipe.
                                    if key == "title":
                                        v = d[key].encode('ascii','ignore')
                                        val_title.append(v)
                                    if key == "calories":
                                        v = d[key]
                                        val_cal.append(v)
                                    if key == "protein":
                                        v = int(re.findall(r'\d+', d[key])[0])
                                        val_prot.append(v)
                                    if key == "carbs":
                                        v = int(re.findall(r'\d+', d[key])[0])
                                        val_carb.append(v)
                                    if key == "fat":
                                        v = int(re.findall(r'\d+', d[key])[0])
                                        val_fat.append(v)
                                    if key == "pricePerServing":
                                        v = round(float(d[key])/100,2)
                                        val_price.append(v)
                                    if key == "readyInMinutes":
                                        v = int(d[key])
                                        val_time.append(v)

                    part2_total = timeit.default_timer() - part2_start
                    s = 'Part 2 time: %f' % (part2_total)
                    strings_timer.append(s)

                inner_total = timeit.default_timer() - inner_start
                s = 'Inner time: %f' % (inner_total)
                strings_timer.append(s)

            # storing recipe's information in several temporary dictionnaries.
            dict_cal_temp = dict(zip(dict_keys, val_cal))
            dict_prot_temp = dict(zip(dict_keys, val_prot))
            dict_carb_temp = dict(zip(dict_keys, val_carb))
            dict_fat_temp = dict(zip(dict_keys, val_fat))
            dict_title_temp = dict(zip(dict_keys, val_title))
            dict_price_temp = dict(zip(dict_keys, val_price))
            dict_time_temp = dict(zip(dict_keys, val_time))

            # storing these dictionnaries for each recipe inside a bigger dictionnary.
            dict_cal[self.recipe_types[recipe_type_index].strip()] = dict_cal_temp
            dict_prot[self.recipe_types[recipe_type_index].strip()] = dict_prot_temp
            dict_carb[self.recipe_types[recipe_type_index].strip()] = dict_carb_temp
            dict_fat[self.recipe_types[recipe_type_index].strip()] = dict_fat_temp
            dict_title[self.recipe_types[recipe_type_index].strip()] = dict_title_temp
            dict_price[self.recipe_types[recipe_type_index].strip()] = dict_price_temp
            dict_time[self.recipe_types[recipe_type_index].strip()] = dict_time_temp

            dict_keys = []
            val_cal = []
            val_prot = []
            val_carb = []
            val_fat = []
            val_title = []
            val_price = []
            val_time = []
            
            # calculating total time taken 
            outer_total = timeit.default_timer() - outer_start
            s = 'Outer loop run %i time: %f' % (recipe_type_index, outer_total)
            strings_timer.append(s)

        # writing those times in a file so they can be looked at later.
        f = open('timer.txt', 'a')
        for s in strings_timer:
            f.write(s)
            f.write('\n')
        f.write('\n')
        f.close()

        return {"json" : response.text, "unique_IDs" : unique_IDs, "url" : req_URL, "dict_cal" : dict_cal, "dict_prot" : dict_prot, "dict_carb" : dict_carb, "dict_fat" : dict_fat, "dict_price" : dict_price, "dict_time" : dict_time, "dict_title" : dict_title, "recipe_types" : self.recipe_types}


class LinearProgrammingSolver(object):
    """The LinearProgrammingSolver class will take every recipes found by the RecipeHandler as well as what the user is searching to optimize
    in order to find the optimal set of recipes responding to the user's needs.
    """

    def __init__(self, obj, obj_nut, dict_prot, dict_fat, dict_cal, dict_carb, dict_title, dict_price, dict_time, recipe_types, daily_nutrients, max_time, asked_recipe_nutrients):
        """This function is used to create the LinearProgrammingSolver object.

        :param obj: If the user wants to maximize or minimize his objective.
        :param obj_nut: The objective the user wants to focus on.
        :param dict_prot: Dictionnary containing the protein provided by every usable recipe for the optimization problem.
        :param dict_fat: Dictionnary containing the fat provided by every usable recipe for the optimization problem.
        :param dict_cal: Dictionnary containing the calories provided by every usable recipe for the optimization problem.
        :param dict_carb: Dictionnary containing the carbohydrates provided by every usable recipe for the optimization problem.
        :param dict_title: Dictionnary containing the titles of every usable recipe for the optimization problem.
        :param dict_price: Dictionnary containing the prices of every usable recipe for the optimization problem.
        :param dict_time: Dictionnary containing the time to cook every usable recipe for the optimization problem.
        :param recipe_types: Dictionnary containing the type of every usable recipe for the optimization problem.
        :param daily_nutrients: Dictionnary containing the nutrients the user asked for.
        :param max_time: The time the user has to cook for this search.
        :param asked_recipe_nutrients: A dictionnary containing the nutrients of the recipe the user specifically asked for.
            (if he asked for one).

        :returns: The LinearProgrammingSolver object we wanted to create.
        """
        self.obj = obj
        self.obj_nut = obj_nut
        self.dict_prot = dict_prot
        self.dict_fat = dict_fat
        self.dict_cal = dict_cal
        self.dict_carb = dict_carb
        self.dict_price = dict_price
        self.dict_time = dict_time
        self.dict_title = dict_title
        self.recipe_types = recipe_types
        self.daily_nutrients = daily_nutrients
        self.max_time = max_time
        self.asked_recipe_nutrients = asked_recipe_nutrients

    def func_lp(self):
        """ This functions tries to returns the optimal list of recipes the user can cook to have the nutrients he asked for.

        :returns: A list of the IDs of the recipes the user should try.
        """

        # setting if it is a minimization or a maximization problem.
        if self.obj == "Max":
            objective = pulp.LpMaximize
        if self.obj == "Min":
            objective = pulp.LpMinimize

        # creating the model to be calculated.
        lp_model = pulp.LpProblem('The Diet Problem', objective)

        # objective function creation with for loop requires an additional variable to add to the model
        obj_lp = 0
        cal_lp = 0
        prot_lp = 0
        fat_lp = 0
        carb_lp = 0
        price_lp = 0
        time_lp = 0

        # creating the objective, considering the user's request.
        if self.obj_nut == "Protein":
            dict_nut = self.dict_prot
        if self.obj_nut == "Fat":
            dict_nut = self.dict_fat
        if self.obj_nut == "Carbs":
            dict_nut = self.dict_carb
        if self.obj_nut == "Calories":
            dict_nut = self.dict_cal
        if self.obj_nut == "Price":
            dict_nut = self.dict_price
        # I think time is not a viable objective anymore but removing these lines could cause errors.
        # We'll take it off when we have the time to test the consequences of removing these lines.
        if self.obj_nut == "Time":
            dict_nut = self.dict_time

        # for every types of recipes:
        for recipe_type_name in self.recipe_types:
            # cleaning possible spaces around the recipe_type name
            recipe_type_name = recipe_type_name.strip()

            vars()['x_' + recipe_type_name] = pulp.LpVariable.dict('x_%s', dict_nut[recipe_type_name].keys(), cat='Binary')
            variable = vars()['x_' + recipe_type_name]

            # objective
            obj_lp += sum(dict_nut[recipe_type_name][key] * variable[key] for key in dict_nut[recipe_type_name].keys())
            lp_model += obj_lp

            # constraint variables
            cal_lp += sum(self.dict_cal[recipe_type_name][key]*variable[key] for key in self.dict_cal[recipe_type_name].keys())
            prot_lp += sum(self.dict_prot[recipe_type_name][key]*variable[key] for key in self.dict_prot[recipe_type_name].keys())
            fat_lp += sum(self.dict_fat[recipe_type_name][key]*variable[key] for key in self.dict_fat[recipe_type_name].keys())
            carb_lp += sum(self.dict_carb[recipe_type_name][key]*variable[key] for key in self.dict_carb[recipe_type_name].keys())
            price_lp += sum(self.dict_price[recipe_type_name][key]*variable[key] for key in self.dict_price[recipe_type_name].keys())
            time_lp += sum(self.dict_time[recipe_type_name][key]*variable[key] for key in self.dict_time[recipe_type_name].keys())

            #constraints
            lp_model += sum([variable[key] for key in self.dict_title[recipe_type_name].keys()]) <= 3

        # setting up constraints
        if self.asked_recipe_nutrients == {}:
            lp_model += cal_lp <= self.daily_nutrients['cal_up']
            lp_model += cal_lp >= self.daily_nutrients['cal_low']
            lp_model += fat_lp >= self.daily_nutrients['fat_low']
            lp_model += fat_lp <= self.daily_nutrients['fat_up']
            lp_model += carb_lp >= self.daily_nutrients['carb_low']
            lp_model += carb_lp <= self.daily_nutrients['carb_up']
            lp_model += prot_lp >= self.daily_nutrients['prot_low']
            lp_model += prot_lp <= self.daily_nutrients['prot_up']
            lp_model += time_lp <= self.max_time
        else:
            # removing asked recipe nutrients from constraints
            lp_model += cal_lp <= self.daily_nutrients['cal_up'] - self.asked_recipe_nutrients['calories']
            lp_model += cal_lp >= self.daily_nutrients['cal_low'] - self.asked_recipe_nutrients['calories']
            lp_model += fat_lp >= self.daily_nutrients['fat_low'] - self.asked_recipe_nutrients['fat']
            lp_model += fat_lp <= self.daily_nutrients['fat_up'] - self.asked_recipe_nutrients['fat']
            lp_model += carb_lp >= self.daily_nutrients['carb_low'] - self.asked_recipe_nutrients['carbs']
            lp_model += carb_lp <= self.daily_nutrients['carb_up'] - self.asked_recipe_nutrients['carbs']
            lp_model += prot_lp >= self.daily_nutrients['prot_low'] - self.asked_recipe_nutrients['protein']
            lp_model += prot_lp <= self.daily_nutrients['prot_up'] - self.asked_recipe_nutrients['protein']
            lp_model += time_lp <= self.max_time - self.asked_recipe_nutrients['time']

        lp_model.solve()

        # if an optimal set of recipes has been found:
        if pulp.LpStatus[lp_model.status] == "Optimal":

            c = 0
            p = 0
            f = 0
            cl = 0
            pr = 0
            t = 0
            suggested_recipes = []

            for recipe_type_name in self.recipe_types:
                recipe_type_name = recipe_type_name.strip()
                # if recipe is part of the optimal list:
                for recipe_ID in self.dict_title[recipe_type_name].keys():
                    if vars()['x_' + recipe_type_name][recipe_ID].value() == 1.0:
                        # putting its ID in the suggested recipes ID
                        suggested_recipes.append(recipe_ID)
                        # adding its nutrients in the dictionnary for the suggested recipes.
                        p += self.dict_prot[recipe_type_name][recipe_ID]
                        c += self.dict_carb[recipe_type_name][recipe_ID]
                        f += self.dict_fat[recipe_type_name][recipe_ID]
                        cl += self.dict_cal[recipe_type_name][recipe_ID]
                        pr += self.dict_price[recipe_type_name][recipe_ID]
                        t += self.dict_time[recipe_type_name][recipe_ID]
            
            # if a peculiar recipe has been asked.
            if self.asked_recipe_nutrients != {}:
                # putting it's id in the suggested recipes id.
                suggested_recipes.append(self.asked_recipe_nutrients["recipe_ID"])
                # adding its nutrients in the dictionnary for the suggested recipes.
                p += self.asked_recipe_nutrients['protein']
                c += self.asked_recipe_nutrients['carbs']
                f += self.asked_recipe_nutrients['fat']
                cl += self.asked_recipe_nutrients['calories']
                t += self.asked_recipe_nutrients['time']
                pr += self.asked_recipe_nutrients['pricePerServing']/100
                

            return {'suggested_recipes' : suggested_recipes, 'total_nutrients_taken' : {'calories' : cl, 'protein' : p, 'carb' : c, 'fat' : f, 'price' : pr, 'time' : t }}
        else:
            return {'suggested_recipes' : [], 'total_nutrients_taken' : {'calories' : 0, 'protein' : 0, 'carb' : 0, 'fat' : 0, 'price' : 0, 'time' : 0 }}


    def get_lp_output(self, suggested_recipes):
        """Function used to get the spoonacular output concerning the recipes suggested by the website.

        :returns: a dictionnary in Json format having all the data about the recipes the user should try.
        """
        diet_recipes = []
        # generating the header necesssary to load the spoonacular page.
        headers = {"X-Mashape-Key": settings.SPOONACULAR_KEY,
                  "Accept": "application/json"}
        # for each suggested recipe:
        for recipe_ID in suggested_recipes:
            # load it's spoonacular page.
            response = requests.get("https://spoonacular-recipe-food-nutrition-v1.p.mashape.com/recipes/" + str(recipe_ID) + "/information?includeNutrition=true",
            headers=headers,
            timeout=100
            )
            # get the information in json format.
            response_text = json.loads(response.text)
            # add this information in the list returned at the end.
            diet_recipes.append(response_text)
        return diet_recipes
