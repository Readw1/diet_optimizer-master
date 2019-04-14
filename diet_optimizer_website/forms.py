from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from .choices import * 
from .models import Feedback
import re


my_default_errors_birthdate = {
    'required': 'This field is required',
    'invalid': 'Enter a valid date. Required format : MM-DD-YYYY'
}

class SignupForm(forms.Form):
    """ Sign up form. Used to allow the user to create an account.

    This form will ask the user for:

    :param username: The user name the user wants to have on the website.
    :param email: The email the website will use to contact the user.
    :param password1: The password the user will be using to connect to the website.
    :param password2: The password is asked twice to verify the user didn't make any typo.

    .. note:: Once filled, this form won't directly create a User. You will need to fill
                The next form for the User to be created.
    """
    error_messages = {
        'password_mismatch': ("Passwords must match."),
        'password_too_short': ("Password must be 6 characters or more."),
        'invalid_email': ("Please enter a valid email address."),
        'username_already_exists' : ("A user with that username already exists."),
        'email_already_exists' : ("A user with that email already exists.")
    }

    username = forms.CharField(label='User name', max_length=100)
    email = forms.CharField(label='Email', max_length=120)
    password1 = forms.CharField(label=("Password"),
        widget=forms.PasswordInput,
        max_length=100)
    password2 = forms.CharField(label=("Confirm password"),
        widget=forms.PasswordInput,
        help_text=("Enter the same password as above, for verification."),
        max_length=100)

    class Meta:
        model = User
        fields = ('username', 'email',)

    def clean_username(self):
        """This function verifies if a User with this name already exists.
        If one does exist it will generate an error.

        :returns: The username entered.
        """
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).first():
            raise forms.ValidationError(
                self.error_messages['username_already_exists'],
                code='username_already_exists',
            )
        return username

    def clean_email(self):
        """This function verifies if it has received something that is an email.
        If not it will generate an error.
        It then verifies if a User with this email already exists.
        If one does exist it will generate an error.

        :returns: The email entered.
        """
        email = self.cleaned_data.get("email")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise forms.ValidationError(
                self.error_messages['invalid_email'],
                code='invalid_email',
            )
        if User.objects.filter(email=email).first():
            raise forms.ValidationError(
                self.error_messages['email_already_exists'],
                code='email_already_exists',
            )
        return email

    def clean_password1(self):
        """This function verifies if the password entered has at least 6 characters.
        Else it will be considered too weak and generate an error.

        :returns: the password entered in the first case.
        """
        password1 = self.cleaned_data.get("password1")
        if len(password1) < 6:
            raise forms.ValidationError(
                self.error_messages['password_too_short'],
                code='password_too_short',
            )
        return password1

    def clean_password2(self):
        """This function verifies if the password entered in password1 and password2
        are the same. If not the user mistyped and the form will generate an error.

        :returns: the password entered in the second case.
        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        """This function will create an user with the username and password given and store it in the database.

        :returns: The user created.
        """
        user = super(SignupForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class PersonalDetailsForm(forms.ModelForm):
    """ Personal details form. Used to get some information about the user's habits and his diet.

    This form will ask the user for:

    :param first_name: The first name of the user.
    :param last_name: The last name of the user.
    :param height: The user's height. (used to calculate bmi)
    :param weight: The user's weight. (used to calculate bmi)
    :param birth_date: The user's birth date. (And thus his age)
    :param activity_level: The user's activity level. (To calculate his nutrients needs)
    :param diet: The user's diet.
    :param gender: The user's gender.
    :param intolerences: The user's intolerences.

    """
    first_name = forms.CharField(label='First name', max_length=100)
    last_name = forms.CharField(label='Last name', max_length=100)
    height =  forms.IntegerField(label ='Height')
    weight = forms.IntegerField(label = 'Weight')
    birth_date = forms.DateField(
        input_formats=['%m-%d-%Y'],
        widget=forms.TextInput(attrs={'placeholder': 'MM-DD-YYYY'}),
        error_messages=my_default_errors_birthdate)
    activity_level = forms.ChoiceField(
        choices=ACTIVITY_LEVEL_CHOICES,
        label="Activity level",
        widget=forms.Select(),
        required=True )
    diet = forms.ChoiceField(
        choices=DIET_CHOICES,
        label="Which diet are you following?",
        widget=forms.Select(),
        required=True)
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        label="Gender",
        widget=forms.Select(),
        required=True)
    intolerences = forms.MultipleChoiceField(
        choices=INTOLERENCES_CHOICES,
        label="Do you have any intolerences?",
        widget=forms.CheckboxSelectMultiple(),
        required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name',)


class LoginForm(forms.Form):
    """ Log in form. Used to allow the user to log onto the website.

    This form will ask the user for:

    :param nick_name: The username of the user.
    :param password: The password of the user.

    .. note:: This form is outdated and not used in the website anymore. We now use django's
              built-in login form.

    """
    error_messages = {
        'empty name': ("Please enter your user name."),
        'empty password': ("Please enter your password."),
        'unexisting user': ("The user you specified is not in our database."),
        'wrong password': ("The password doesn't match with the user."),
    }

    nick_name = forms.CharField(label="User name",
                                max_length=100)
    password = forms.CharField(label="Password",widget=forms.PasswordInput,)

    def clean_nick_name(self):
        """This function will get the username and check if a user with this username is in the database.
        If there is none or if the username given is not correct it will raise an error.

        :returns: The nick_name entered
        """
        nick_name = self.cleaned_data.get("nick_name")
        user = User.objects.filter(username=nick_name).first()
        if user is None:
            raise forms.ValidationError(
                self.error_messages['unexisting user'],
                code='unexisting user',
            )
        if nick_name=="":
            raise forms.ValidationError(
                self.error_messages['empty name'],
                code='empty name',
            )
        return nick_name

    def clean_password(self):
        """This function will get the password entered and verify it for the username entered.

        If the password and user doesn't match or if no password was entered it will raise an error.

        :returns: The password entered.
        """
        password = self.cleaned_data.get("password")
        nick_name = self.cleaned_data.get("nick_name")
        user = User.objects.filter(username=nick_name).first()
        if not user==None:
            if not user.check_password(password):
                raise forms.ValidationError(
                    self.error_messages['wrong password'],
                    code='wrong password',
                )
        if password=="":
            raise forms.ValidationError(
                self.error_messages['empty password'],
                code='empty password',
            )
        return password


class PasswordResetRequestForm(forms.Form):
    """ Password reset form. Used to allow the user to change is password if he forgot it.

    This form will ask the user for:

    :param email: The user's email.

    """
    email = forms.CharField(label='Email', max_length=120)

    def clean_email(self):
        """This function will get the email entered and check if it has an email regular expression.
        If not it will raise an error.

        :returns: The email entered.
        """
        email = self.cleaned_data.get("email")

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise forms.ValidationError(
                self.error_messages['invalid_email'],
                code='invalid_email',
            )
        return email


class SettingsForm(forms.Form):
    """ Settings form. Used to allow the user to change his personal settings.

    This form will ask the user for:

    :param height: The user's height. (used to calculate bmi)
    :param weight: The user's weight. (used to calculate bmi)
    :param birth_date: The user's birth date. (And thus his age)
    :param gender: The user's gender.

    """
    height = forms.IntegerField(label='Height')
    weight = forms.IntegerField(label='Weight')
    birth_date = forms.DateField(
        input_formats=['%m-%d-%Y'],
        widget=forms.TextInput(attrs={'placeholder': 'MM-DD-YYYY'}),
        error_messages=my_default_errors_birthdate)
    gender = forms.ChoiceField( choices=GENDER_CHOICES,
                                label="Gender",
                                widget=forms.Select())


class AccountSettingsForm(forms.Form):
    """ Account settings form. Allows the user to change his password simply.

    This form will ask the user for:

    :param new_password: The user's new password.
    :param new_password2: The new password is asked twice to verify the user didn't do any typo.

    """
    error_messages = {
        'password_mismatch': ("Passwords must match."),
        'password_too_short': ("Password must be 6 characters or more."),
    }
    new_password = forms.CharField(label=("Password"),
        widget=forms.PasswordInput,
        max_length=100)
    new_password2 = forms.CharField(label=("Confirm password"),
        widget=forms.PasswordInput,
        help_text=("Enter the same password as above, for verification."),
        max_length=100)

    class Meta:
        model = User
        fields = ('username', 'email',)

    def clean_new_password(self):
        """This function verifies if the password entered has at least 6 characters.
        Else it will be considered too weak and generate an error.

        :returns: The new password entered in the first case.
        """
        new_password = self.cleaned_data.get("new_password")

        if len(new_password) < 6:
            raise forms.ValidationError(
                self.error_messages['password_too_short'],
                code='password_too_short',
            )
        return new_password

    def clean_new_password2(self):
        """This function verifies if the password entered in new_password and new_password2
        are the same. If not the user mistyped and the form will generate an error.

        :returns: The new password entered in the second case.
        """
        new_password = self.cleaned_data.get("new_password")
        new_password2 = self.cleaned_data.get("new_password2")

        if new_password and new_password2 and new_password != new_password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return new_password2

class TogglePopUpForm(forms.Form):
    """ Toggle popups form. Allows the user to choose if he wants to receive popups from the
    website or not.

    This form will ask the user for:

    :param accept_popup: Boolean representing if the user wants popups (True) or not (False)

    """
    accept_popup = forms.BooleanField(label=("Do you allow the website to inform you with popups?"),
                                    widget=forms.CheckboxInput(),
                                    required=False)


class GetRecipeForm(forms.Form):
    """ Get recipe form. This form asks for all the information necessary to ask recipes to the website.

    This form will ask the user for:
    
    :param cuisines: List of types of cuisines the user agrees to eat. (ex: mexican, japanese,...)
    :param recipeTypes: List of types if dishes the user wants to eat. (ex: deserts, main dish,...)
    :param rawGroups: Raw kinds of foods the user agrees to eat. (ex: veal products, sweets,...)
    :param objectiveNutrition: What nutrient does the user wants to focus on. (ex: carbs, fat,...)
    :param objectiveMinMax: If the user wants to maximize this nutrient or minimize it.
    :param calLow: Minimum amount of calories the user wants to have.
    :param calUp: Maximum amount of calories the user wants to have.
    :param carbLow: Minimum amount of carbohydrates the user wants to have.
    :param carbUp: Maximum amount of carbohydrates the user wants to have.
    :param protLow: Minimum amount of proteins the user wants to have.
    :param protUp: Maximum amount of proteins the user wants to have.
    :param fatLow: Minimum amount of fat the user wants to have.
    :param fatUp: Maximum amount of fat the user wants to have.
    :param time: The Maximum time the user has to cook.

    """
    error_messages = {
        'empty_cuisines': ("Please select a type of cuisine."),
        'empty_recipeTypes': ("Please select a type of recipe."),
        'empty_rawGroups': ("Please select a type of food."),
        'unknown_objectiveNutrition': ("Please tell us what you would like to focus on."),
        'unknown_objectiveMinMax': ("We don't know if you want to minimize or maximize your objective.")
    }

    cuisines = forms.MultipleChoiceField(choices=CUISINES_CHOICES,
                                        label='Which cuisine(s) would you like to include?',
                                        widget=forms.CheckboxSelectMultiple())
    recipeTypes = forms.MultipleChoiceField(choices=RECIPE_TYPES_CHOICES,
                                            label='What kind of recipes do you want?',
                                            widget=forms.CheckboxSelectMultiple())
    rawGroups = forms.MultipleChoiceField(choices=RAW_GROUPS_CHOICES,
                                        label='What kind of group foods do you want?',
                                        widget=forms.CheckboxSelectMultiple())
    objectiveNutrition = forms.ChoiceField(choices=OBJECTIVES_CHOICES,
                                            label='What would you like to focus on?',
                                            widget=forms.RadioSelect(),
                                            initial='Calories',
                                            required = True)
    objectiveMinMax = forms.ChoiceField(choices=MIN_MAX_CHOICES,
                                        label='Do you want to maximize or minimize that?',
                                        widget=forms.RadioSelect(),
                                        initial='Min',
                                        required = True)
    calLow = forms.CharField()
    calUp = forms.CharField()
    carbLow = forms.CharField()
    carbUp = forms.CharField()
    protLow = forms.CharField()
    protUp = forms.CharField()
    fatLow = forms.CharField()
    fatUp = forms.CharField()
    time = forms.IntegerField(label="How much time do you have to cook?(in minutes)",
                            initial=30)

    def __init__(self, user, *args, **kwargs):
        """ Initialization function. Whenever created, this form needs to have the user as an argument.

        :param user: The user who's favorite recipes we want to gather.
        
        When creating, it will initialize all the fields stated previously.
        It will then load the name of the recipes the user liked.
        It will take these names to put them as possible choices for a last field called peculiar recipe.

        This field represents a peculiar recipe the user would like to have in addition with what the
        website will load.

        :returns: The form we wanted to create.
        """
        super(GetRecipeForm, self).__init__(*args, **kwargs)
        user_good_feedback = Feedback.objects.filter(user=user,mark=1)
        user_liked_recipes = [('None',('None'))]
        for feedback in user_good_feedback:
            title = feedback.recipe.title
            user_liked_recipes.append((title,(title)))
        self.fields['peculiar_recipe'] = forms.ChoiceField(
                                        label='Is there any recipe you would like to include again?',
                                        widget=forms.Select(),
                                        initial="None",
                                        required=False,
                                        choices=tuple(user_liked_recipes))


    def clean_cuisines(self):
        """This function verifies if the cuisines field has been properly filled.
        Else it will generate an error.

        :returns: the list of the cuisines that the user asked for.
        """
        cuisines = self.cleaned_data.get("cuisines")

        if cuisines is None:
            raise forms.ValidationError(
                self.error_messages['empty_cuisines'],
                code='empty_cuisines',
            )
        return cuisines

    def clean_recipeTypes(self):
        """This function verifies if the recipeTypes field has been properly filled.
        Else it will generate an error.

        :returns: The list of the recipeTypes the user asked for.
        """
        recipeTypes = self.cleaned_data.get("recipeTypes")

        if recipeTypes is None:
            raise forms.ValidationError(
                self.error_messages['empty_recipeTypes'],
                code='empty_recipeTypes',
            )
        return recipeTypes

    def clean_rawGroups(self):
        """This function verifies if the rawGroups field has been properly filled.
        Else it will generate an error.

        :returns: The list of the raw groups of foods the user asked for.
        """
        rawGroups = self.cleaned_data.get("rawGroups")

        if rawGroups is None:
            raise forms.ValidationError(
                self.error_messages['empty_rawGroups'],
                code='empty_rawGroups',
            )
        return rawGroups

    def clean_objectiveNutrition(self):
        """This function verifies if the objectiveNutrition field has been properly filled.
        Else it will generate an error.

        :returns: The nutrition objective the user wants to focus on.
        """
        objectiveNutrition = self.cleaned_data.get("objectiveNutrition")

        if objectiveNutrition is None:
            raise forms.ValidationError(
                self.error_messages['unknown_objectiveNutrition'],
                code='unknown_objectiveNutrition',
            )
        return objectiveNutrition

    def clean_objectiveMinMax(self):
        """This function verifies if the objectiveMinMax field has been properly filled.
        Else it will generate an error.

        :returns: If the user wants to maximize or minimize its objective.
        """
        objectiveMinMax = self.cleaned_data.get("objectiveMinMax")

        if objectiveMinMax is None:
            raise forms.ValidationError(
                self.error_messages['unknown_objectiveMinMax'],
                code='unknown_objectiveMinMax',
            )
        return objectiveMinMax

class UserProfileForm(forms.Form):
    """ User profile form. This form allows the user to change all his settings concerning his diet and the recipes he prefers.

    This form will ask the user for:
    
    :param activity_level: The user's activity level.
    :param diet: The user's diet.
    :param intolerences: The list of the user's intolerences.
    :param cuisines: The User's favorite types of cuisines.
    :param rawGroups: The user's favorite types of raw foods.
    :param timetoCook: The user's usual time he has to cook.

    """
    activity_level = forms.ChoiceField(
        choices=ACTIVITY_LEVEL_CHOICES,
        label="Activity level",
        widget=forms.Select(),
        required=True )
    diet = forms.ChoiceField(choices=DIET_CHOICES,
                             label="Which diet are you following?",
                             widget=forms.Select())
    intolerences =forms.MultipleChoiceField(choices=INTOLERENCES_CHOICES,
                                    label='Do you have any intolerences?',
                                    widget=forms.CheckboxSelectMultiple())
    cuisines = forms.MultipleChoiceField(choices=CUISINES_CHOICES,
                                        label='Which cuisine(s) do you prefer?',
                                        widget=forms.CheckboxSelectMultiple(),
                                        required=False)
    rawGroups = forms.MultipleChoiceField(choices=RAW_GROUPS_CHOICES,
                                        label='What kind of group foods do you prefer?',
                                        widget=forms.CheckboxSelectMultiple(),
                                        required=False)
    timeToCook = forms.IntegerField(label="How much time do you usually have to cook?")
