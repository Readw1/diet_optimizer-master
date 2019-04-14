from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from django.contrib.auth import logout
from django.contrib import messages
from django.template import RequestContext
from django.shortcuts import render, redirect
from django.http import Http404
from django.db import transaction
from .lists.cuisines_and_foodgroups import get_cuisines, get_foodgroups
from .models import *
from .forms import *
import sys
import random


# Create your views here.

def home(request):
    """ Home view.

    This view doesn't do much. However django needs a home view to function properly.
    """
    return render(request, 'diet_optimizer_website/index.html')


def index(request):
    """ Index view.

    This view only renders the index template, which corresponds to the first page the user will see on the website.
    """
    return render(request, 'diet_optimizer_website/index.html')



# @app.route('/signup', methods=['GET', 'POST']) ?
# @cross_origin() ?
def signup(request):
    """ User creation view.

    This view corresponds to the first part of the sign up process.
    If it is accessed via GET method it will simply load the first signup form and render the page.
    If it is accessed via POST method, it will read the information send via the sign up form and
    check if it is valid.
    If the information is valid it will create a dictionnary containing the user's information and 
    send it to the next signup step.
    If the information is not valid however it will re-render the page asking to fill the form correctly. 
    """
    if 'username' in request.session:        
        return redirect('profile')

    if request.method == 'POST':
        # loads POST data in the form
        form = SignupForm(request.POST)

        # checks if the form is filled correctly and creates the "cleaned_data"
        if form.is_valid():
            try:
                # creates a dictionnary with all the user's data.
                user_dict = {
                    'username' : form.cleaned_data.get("username"),
                    'email' : form.cleaned_data.get("email"),
                    'password' : form.cleaned_data.get("password1")}
                # storing the dictionary in the session data.
                request.session['user_for_personal_details_page'] = user_dict
                # redirecting to the second part of sign in.
                return redirect('personal_details')

            except :
                print("Unexpected error:", sys.exc_info()[0])
                raise

        else:
            # if not filled properly we lead the user back to the page.
            return render(request, 'diet_optimizer_website/signup.html', {'form': form})

    elif request.method == 'GET':
        form = SignupForm()
        return render(request, 'diet_optimizer_website/signup.html', {'form': form})


def personal_details(request):
    """ User information  to create a new user.

    This view corresponds to the second part of the sign up process.
    If it is accessed via GET method, it will simply load the personal details form and render the page.
    If it is accessed via POST method, it will read the information send via the personal details form and
    check if it is valid.

    If the information is valid, it will read the user details sent by the signup view (above) and create a User
    with this data. Then it will create a UserDB object linked to the User just created. It will then fill all
    the necessary informations given concerning both the User and the UserDB.
    Next it will read the intolerences and for each, create an Intolerence object with the User and the name.
    Finally it will redirect the user to the login page.

    If the information is not valid however it will re-render the page asking to fill the form correctly. 
    """
    if 'username' in request.session:
        return redirect('profile')
    if request.method == 'POST':
        # loads POST data in the form 
        form = PersonalDetailsForm(request.POST)

        # checks if the form is filled correctly and creates the "cleaned_data"
        if form.is_valid():
            try:
                # transaction.atomic allows the database altering algorithms to happen all at once
                # avoiding mismatch in the database savend datas.
                with transaction.atomic():
                    # getting the data entered in the previous view through session data.
                    user_dict = request.session.get('user_for_personal_details_page')
                    # creation of the User.
                    user = User.objects.create_user(
                        username=user_dict.get('username'),
                        email=user_dict.get('email'),
                        password=user_dict.get('password')
                    )
                    # creation of a UserDB oject connected to the newly created user.
                    userdb = UserDB.objects.create(user=user)

                    # setting up his first and last name. 
                    user.last_name = form.cleaned_data.get("last_name")
                    user.first_name = form.cleaned_data.get("first_name")

                    # if statement allows to enter data differently depending on the weight unit the user used.
                    if request.POST.get("weightunit") == "lbs":
                        userdb.weight = form.cleaned_data.get("weight") / 2.20462
                    else:
                        userdb.weight = form.cleaned_data.get("weight")

                    # if statement allows to enter data differently depending on the height unit the user used.
                    if request.POST.get("heightunit") == "in":
                        userdb.height = form.cleaned_data.get("height") / 0.393701
                    else:
                        userdb.height = form.cleaned_data.get("height")

                    # setting up various data about the user. Variable names should be explicit enough.
                    userdb.birth_date = form.cleaned_data.get("birth_date")
                    userdb.activity_level = form.cleaned_data.get("activity_level")
                    userdb.diet = form.cleaned_data.get("diet")
                    userdb.gender = form.cleaned_data.get("gender")

                    # add each element of the intolerence list in the database. For that we create one new Intolerence object for each.
                    intolerences = form.cleaned_data.get("intolerences")
                    for intolerence in intolerences :
                        new_intolerence = Intolerences.objects.create(
                            userdb=userdb,
                            intolerence_name=intolerence)

                    # saving the new objects created and updated in the database.
                    user.save()
                    userdb.save()
                    request.session.pop('user_for_personal_details_page')

                    # once the account is created we ask the user to login.
                    return redirect('login')


            except:
                print("Unexpected error:", sys.exc_info()[0])
                raise

            else:
                # at the end the transaction must be committed to confirm it, thus ending the transaction.atomic() statement.
                transaction.commit()

        else:
            # if it is not filled properly we lead the user back to the page.
            return render(request, 'diet_optimizer_website/personal_details.html', {'form': form})

    elif request.method == 'GET':
        # loading a form to display it in the page.
        form = PersonalDetailsForm()
        return render(request, 'diet_optimizer_website/personal_details.html', {'form': form})


def about(request):
    """ About view

    This view simply renders the about page, giving information about the website to the users.
    """    
    return render(request, 'diet_optimizer_website/about.html')

def about_logged_in(request):
    """ About view

    This view simply renders the about page, giving information about the website to the users.
    """ 
    return render(request, 'diet_optimizer_website/about_logged_in.html')


# def login(request):
#     """ Log in view

#     This view is outdate, we now use the django build in login view.
#     """ 
#     if 'username' in request.session:
#         return redirect('profile')

#     form = LoginForm()

#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data.get("nick_name")
#             password = form.cleaned_data.get("password")
#             user = User.objects.filter(username=username).first()
#             if user is not None and user.check_password(password):
#                 user = authenticate(username=username, password=password)
#                 request.session['username'] = username
#                 return redirect('profile')
#             else:
#                 if user is None:
#                     request.session['user'] = None
#                 if not(user.check_password(password)):
#                     request.session['wrong_password']=True
#                 return redirect('login')
#         else:
#             return render(request, 'diet_optimizer_website/login.html', {'form': form})
#     elif request.method == 'GET':
#         return render(request, 'diet_optimizer_website/login.html', {'form': form})


def logout_view(request):
    """ Logout view.

    This view simply logs out the user and redirects him to the index page.
    """ 
    logout(request)
    return redirect('index')


def profile(request):
    """ Profile view.

    This view will simply load all the information about the user and send them to the page.
    """ 
    user = request.user
    userDB = user.userdb
    intolerences = Intolerences.objects.filter(userdb=userDB)
    userData = UserData(user)
    return render(request, 'diet_optimizer_website/profile.html', {'user': user,
                                                                   'userDB': userDB,
                                                                   'intolerences': intolerences,
                                                                   'userData': userData})


def personal_settings(request):
    """ personal settings view

    This view allows the user to change his personal settings like gender, birth_date or weight and height, etc.
    It will first load the user's data and put them in the settings form. (this allows the form to be initially 
    filled with the user's data).
    If the view is accessed via GET method it will simply render the page.
    If the view is accessed via POST method it will fill the form with the posted data and check if it is valid.
    If the data is valid it will change all the entered data to update the user's information.
    If the data is not valid however it will reload the page and ask the user to enter data properly.
    """ 
    user = request.user
    userDB = user.userdb
    
    # loads the user's birth date in the right format. month-day-year (american format due to the public)
    birth_date_formated = userDB.birth_date.strftime("%m-%d-%Y")
    # loading a SettingForm with the user's data already entered.
    # This will both allow the user to see his current data and to not have to re-enter everything.
    form = SettingsForm(initial={'height': userDB.height,
                                  'weight': userDB.weight,
                                  'gender': userDB.gender,
                                  'birth_date': birth_date_formated})

    if request.method == 'POST':
        # loads post data in the form.
        form = SettingsForm(request.POST)

        # checks if the form is properly filled and create "cleaned_data"
        if not form.is_valid():
            return render(request, 'diet_optimizer_website/personal_settings.html',
                          {'form': form, 'response': {'user_info': {'birthdate' : userDB.birth_date,
                                                                    'weight': userDB.weight,
                                                                    'height': userDB.height,
                                                                    'gender': userDB.gender,
                                                                    'activitylevel': userDB.activity_level,
                                                                    'diet': userDB.diet}}})
        else:
            # updates the user's weight according to the weight unit he used.
            if request.POST.get("weightunit") == "lbs":
                userDB.weight = form.cleaned_data.get("weight") / 2.20462
            else:
                userDB.weight = form.cleaned_data.get("weight")

            # updates the user's height according to the height unit he used.
            if request.POST.get("heightunit") == "in":
                userDB.height = form.cleaned_data.get("height") / 0.393701
            else:
                userDB.height = form.cleaned_data.get("height")

            # updates the user's gender and birth date.
            userDB.birth_date = form.cleaned_data.get("birth_date")
            userDB.gender = form.cleaned_data.get("gender")
            # saves the changes rencently made.
            userDB.save()
            return redirect('profile')

    elif request.method == 'GET':
        return render(request, 'diet_optimizer_website/personal_settings.html',
                      {'form': form, 'response': {'user_info': {'birthdate' : userDB.birth_date,
                                                                'weight': userDB.weight,
                                                                'height': userDB.height,
                                                                'gender': userDB.gender,
                                                                'activitylevel': userDB.activity_level,
                                                                'diet': userDB.diet}}})


def user_profile(request):
    """ personal settings view

    This view allows the user to change his preferences, objectives and intolerences.
    It will first load the user's data, intolerences and favorites and put them in the settings form. 
    (this allows the form to be initially filled with the user's data).
    If the view is accessed via GET method it will simply render the page.
    If the view is accessed via POST method it will fill the form with the posted data and check if it is valid.
    If the data is valid it will change all the entered data to update the user's information.
    If the data is not valid however it will reload the page and ask the user to enter data properly.
    """
    user = request.user
    userDB = user.userdb

    # gathering user's intolerences
    intolerences = Intolerences.objects.filter(userdb=userDB)
    intolerences_name_list = []
    for intolerence in intolerences:
        intolerences_name_list.append(intolerence.intolerence_name)

    # gathering user's favorite cuisines
    favorite_cuisines = PreferenceCuisines.objects.filter(userdb=userDB)
    favorite_cuisines_list = []
    for favorite_cuisine in favorite_cuisines:
        favorite_cuisines_list.append(favorite_cuisine.cuisine_name)

    # gathering user's favorite raw foods
    favorite_raw_foods = PreferenceRawFoods.objects.filter(userdb=userDB)
    favorite_raw_foods_list = []
    for favorite_raw_food in favorite_raw_foods:
        favorite_raw_foods_list.append(favorite_raw_food.raw_food_name)

    # crating a form already filled with user's current preferences and data.
    form = UserProfileForm(initial={'activity_level': userDB.activity_level,
                                  'diet': userDB.diet,
                                  'intolerences': intolerences_name_list,
                                  'cuisines': favorite_cuisines_list,
                                  'rawGroups': favorite_raw_foods_list,
                                  'timeToCook': userDB.timeToCook})

    if request.method == 'POST':
        # loads post data in the form.
        form = UserProfileForm(request.POST)

        # checks if form is filled properly and creates "cleaned_data".
        if not form.is_valid():
            return render(request, 'diet_optimizer_website/user_profile.html', {'form': form, 'intolerences_name_list':intolerences_name_list})
        else:
            
            # updating user's activity level, diet and time he usually has to cook.
            userDB.activity_level = form.cleaned_data.get("activity_level")
            userDB.diet = form.cleaned_data.get("diet")
            userDB.timeToCook = form.cleaned_data.get("timeToCook")
            userDB.save()

            # resetting all intolerences with new informations
            # deleting current intolerences for the user
            intolerences = Intolerences.objects.filter(userdb=userDB)
            intolerences.delete()
            # creating all the new intolerences
            intolerences = form.cleaned_data.get("intolerences")
            for intolerence in intolerences:
                Intolerences.objects.create(userdb=userDB, intolerence_name=intolerence)

            # resetting all cuisine preferences with new informations
            # deleting current cuisine preferences for the user
            cuisine_preferences = PreferenceCuisines.objects.filter(userdb=userDB)
            cuisine_preferences.delete()
            # creating all the new cuisine preferences
            cuisine_preferences = form.cleaned_data.get("cuisines")
            for cuisine_preference in cuisine_preferences:
                PreferenceCuisines.objects.create(userdb=userDB, cuisine_name=cuisine_preference)

            # resetting all raw food preferences with new informations
            # deleting current raw food preferences for the user
            raw_food_preferences = PreferenceRawFoods.objects.filter(userdb=userDB)
            raw_food_preferences.delete()
            # creating all the new raw food preferences
            raw_food_preferences = form.cleaned_data.get("rawGroups")
            for raw_food_preference in raw_food_preferences:
                PreferenceRawFoods.objects.create(userdb=userDB, raw_food_name=raw_food_preference)
            return redirect('profile')

    elif request.method == 'GET':
        return render(request, 'diet_optimizer_website/user_profile.html', {'form': form, 'intolerences_name_list':intolerences_name_list})


def account_settings(request):
    """ Account settings view

    This view allows the user to change his password, or the fact that he can receive popups or not.
    It will first load the user's data.
    If the view is accessed via GET method it will simply load both forms and render the page.
    If the view is accessed via POST method it will fill first check which form has been filled.
    For each form, if it has been filled it will check if the data has been correctly entered.
    If the data is valid it will create a confirmation message and change all the entered data to update the user's information.
    If the data is not valid however it will create an error message and reload the page and ask the user to enter data properly.
    """
    user = request.user
    userDB = user.userdb

    if request.method == 'POST':
        # loading post data in the forms.

        # account form is to change the user's password
        account_form = AccountSettingsForm(request.POST)

        # popup form is to ask if the user wants to receive popups from de website.
        popup_form = TogglePopUpForm(request.POST)

        # if statement checks if popup_form is filled
        if 'popups' in request.POST:
            # checks if form is properly filled and creates "cleaned_data"
            if popup_form.is_valid():
                # sets if user wants to have popups.
                userDB.accepts_popups = popup_form.cleaned_data.get("accept_popup")
                # save potential changes.
                userDB.save()
                if userDB.accepts_popups:
                    messages.success(request, 'From now on the website will inform you via popups sometimes.')
                else:
                    messages.success(request, 'You will no longer receive popups.')
                return render(request, 'diet_optimizer_website/account_settings.html', {'account_form': account_form,
                                                                            'popup_form': popup_form})
            else:
                # if form not properly filled the website will inform the user via message.
                messages.error(request, 'There was an error in your informations.')
                return render(request, 'diet_optimizer_website/account_settings.html', {'account_form': account_form,
                                                                                    'popup_form': popup_form})

        # if statement checks if account_form is filled
        if 'password' in request.POST:
            # checks if form is properly filled and creates "cleaned_data"
            if account_form.is_valid():
                # changes user's password.
                new_password = account_form.cleaned_data.get("new_password")
                user.set_password(new_password)
                # saves changes.
                user.save()
                # weirdly, changing the password disconnects the user...
                # authenticate tries to reconnect him but it's not succeeding. Leaving this here if someone wants to look further into it.
                user = authenticate(username=user.username, password=new_password)
                messages.success(request, 'Your password was updated successfully!')
                return redirect('account_settings')
            else:
                messages.error(request, 'There was an error in your informations.')
                return render(request, 'diet_optimizer_website/account_settings.html', {'account_form': account_form,
                                                                                    'popup_form': popup_form})


    elif request.method == 'GET':
        account_form = AccountSettingsForm()
        popup_form = TogglePopUpForm(initial={'accept_popup': userDB.accepts_popups})
        return render(request, 'diet_optimizer_website/account_settings.html', {'account_form': account_form,
                                                                                'popup_form': popup_form})


def history_not_tried(request):
    """ History not tried view

    This view allows the user to see all the recipes and raw foods the website advised him to try.
    It will first load all the Feedback objects linked to the user. 
    Then it will load all the data about the recipes and the raw foods in the feedbacks.
    If the view is accessed via GET method it will simply render the page.
    If the view is accessed via POST method it will check for each recipe and raw food if its mark changed.
    If it did change it will update the number of likes and dislikes it currently has.
    Then it will update accordingly it's percentage of likes.
    """
    user = request.user
    userDB = user.userdb


    #feedbacks = Feedback.objects.all()
    feedbacks = Feedback.objects.filter(user=userDB)
    #.order_by('mark')
    # uid = user.uid
    #form.recipe.choices = [(Recipe.query.filter_by(rid=i.rid).first().name, Recipe.query.filter_by(rid=i.rid).first().name) for i in feed_back]

    recipes_name = [feedback.recipe.title for feedback in feedbacks]
    # getting every recipe links grom the loaded feedbacks.
    recipes_link = [feedback.recipe.link for feedback in feedbacks]


    #feedbacks_raw_food = FeedbackRawFood.objects.all()
    # feedback = Feedback.objects.filter(user=user).first() ?

    # loads every food feedbacks linked to the user.
    feedbacks_raw_food = FeedbackRawFood.objects.filter(user=userDB)
    #.order_by('mark')

    # loads every food from the loaded feedbacks with a mark of 4. (corresponds to not yet tried foods.)
    raw_foods = [feedback_raw_food.food for feedback_raw_food in feedbacks_raw_food if feedback_raw_food.mark == 4]

    # loads the names of the foods previously selected.
    raw_foods_name = [feedback_raw_food.food.desc for feedback_raw_food in feedbacks_raw_food]

    # loads every notes of each recipe feedbacks previously loaded.
    marks = [feedback.mark for feedback in feedbacks]
    # loads all the recipes that have not yet een tried in the use'rs recipe feedbacks.
    recipes = [feedback.recipe for feedback in feedbacks if feedback.mark == 4]

    if request.method == 'POST':
        # for each recipes not tried by the user but advised by the website :
        for recipe in recipes:
            # getting the data posted for this recipe concerning its mark and casting it into an integer.
            # (cast is important because post data gives strings)
            new_mark = int(request.POST.get(str(recipe.pk)))

            # getting user's previous feedback concerning this recipe.
            feedback_modified = Feedback.objects.filter(user=userDB, recipe=recipe).first()
            # checking if the user changed his mind concerning the recipe.
            if not(feedback_modified.mark == new_mark):
                print(new_mark)
                if new_mark == 1:
                    # if now he likes it the recipe gets one more like.
                    recipe.likes = recipe.likes + 1
                elif new_mark == 2 or new_mark == 3:
                    # if now he doesn't  he gets one more dislike (or no opinion)
                    recipe.dislikes_no_opinion = recipe.dislikes_no_opinion + 1
                if (recipe.likes + recipe.dislikes_no_opinion) > 0:
                    # calculating the percentage of likes concerning the recipe.
                    recipe.percent = (recipe.likes / (recipe.likes + recipe.dislikes_no_opinion)) * 100
                else:
                    recipe.percent = 0
                # changing the mark.
                feedback_modified.mark = new_mark
                # saving changes on the feedback and recipe.
                feedback_modified.save()
                recipe.save()
        for raw_food in raw_foods:
            # process here is exactly the same as with recipes. Check above to see how it works.
            new_mark = int(request.POST.get(str(raw_food.NDB_No)))
            feedback_raw_food_modified = FeedbackRawFood.objects.filter(food=raw_food).first()
            if not(feedback_raw_food_modified.mark == new_mark):
                # if new_mark == 1:
                #     raw_food.likes = raw_food.likes + 1
                # elif new_mark == 2 or new_mark == 3:
                #     raw_food.dislikes_no_opinion = raw_food.dislikes_no_opinion + 1
                # if (raw_food.likes + raw_food.dislikes_no_opinion) > 0:
                #     raw_food.percent = (raw_food.likes / (raw_food.likes + raw_food.dislikes_no_opinion)) * 100
                # else:
                #     raw_food.percent = 0
                # raw_food.save()

                feedback_raw_food_modified.mark = new_mark
                feedback_raw_food_modified.save()
        return redirect('history_not_tried')

    elif request.method == 'GET':
        return render(
            request,
            'diet_optimizer_website/history_not_tried.html',
            {'recipes_name' : recipes_name,
            'recipes_link' : recipes_link,
            'marks' : marks,
            'recipes' : recipes,
            'feedbacks' : feedbacks,
            'feedbacks_raw_food' : feedbacks_raw_food,
            'raw_foods' : raw_foods,
            'raw_foods_name' : raw_foods_name})


def history_tried(request):
    """ History of tried recipes view

    This view allows the user to see all the recipes and raw foods he tried.
    It will first load all the Feedback objects linked to the user. 
    Then it will load all the data about the recipes and the raw foods in the feedbacks.
    If the view is accessed via GET method it will simply render the page.
    If the view is accessed via POST method it will check for each recipe and raw food if its mark changed.
    If it did change it will update the number of likes and dislikes it currently has.
    Then it will update accordingly it's percentage of likes.
    """
    user = request.user
    userDB = user.userdb

    # loading every recipe feedback concerning the user.
    feedbacks = Feedback.objects.filter(user=userDB)

    # loading names and links of the recipes concerning the previously loaded feedbacks.
    recipes_name = [feedback.recipe.title for feedback in feedbacks]
    recipes_link = [feedback.recipe.link for feedback in feedbacks]

    # loading every food feedback concerning the user.
    feedbacks_raw_food = FeedbackRawFood.objects.filter(user=userDB)

    # loading foods concerning the previously loaded feedbacks, only if their mark is different than 4 (not tried yet).
    raw_foods = [feedback_raw_food.food for feedback_raw_food in feedbacks_raw_food if feedback_raw_food.mark != 4]
    # loading names and links of the foods previously loaded.
    raw_foods_name = [feedback_raw_food.food.desc for feedback_raw_food in feedbacks_raw_food]

    # loading every mark of the loaded recipe feedbacks.
    marks = [feedback.mark for feedback in feedbacks]

    # loads recipes of the feedbacks, only if mark is not 4.
    recipes = [feedback.recipe for feedback in feedbacks if feedback.mark != 4]

    if request.method == 'POST':
        for recipe in recipes:
            # getting the data posted for this recipe concerning its mark and casting it into an integer.
            # (cast is important because post data gives strings)
            new_mark = int(request.POST.get(str(recipe.pk)))

            # loading previous feedback from the user on this peculiar recipe.
            feedback_modified = Feedback.objects.filter(user=userDB, recipe=recipe).first()
            # if the mark changed:
            if not(feedback_modified.mark == new_mark):
                # if now the user likes it
                if new_mark == 1:
                    # recipe gets one more like
                    recipe.likes = recipe.likes + 1
                    # if recipe used to be not liked, he gets one less dislike.
                    if feedback_modified.mark == 2 or feedback_modified.mark == 3:
                        recipe.dislikes_no_opinion = recipe.dislikes_no_opinion - 1
                # if now user doen't like it (or doesn't care)
                elif new_mark == 2 or new_mark == 3:
                    # recipe gets one more unlike.
                    recipe.dislikes_no_opinion = recipe.dislikes_no_opinion + 1
                    # if recipe used to be liked
                    if feedback_modified.mark == 1:
                        # recipe gets one less like.
                        recipe.likes = recipe.likes - 1
                # if user now says he never tried the recipe (because he miss clicked)
                elif new_mark == 4:
                    # if recipe used to be liked
                    if feedback_modified.mark == 1:
                        # recipe has one less like.
                        recipe.likes = recipe.likes - 1
                    # if recipe used to be disliked
                    elif feedback_modified.mark == 2 or feedback_modified.mark == 3:
                        # recipe gets one less dislike.
                        recipe.dislikes_no_opinion = recipe.dislikes_no_opinion - 1
                if (recipe.likes + recipe.dislikes_no_opinion) > 0:
                    # calculating recipe's new percentage of likes.
                    recipe.percent = (recipe.likes / (recipe.likes + recipe.dislikes_no_opinion)) * 100
                else:
                    recipe.percent = 0
                # changing recies mark on this feedback.
                feedback_modified.mark = new_mark
                # saving changes.
                feedback_modified.save()
                recipe.save()
        for raw_food in raw_foods:
            # process works exactly like fro recipes. Please check above to see how it works.
            new_mark = int(request.POST.get(str(raw_food.NDB_No)))
            feedback_raw_food_modified = FeedbackRawFood.objects.filter(food=raw_food).first()
            if not(feedback_raw_food_modified.mark == new_mark):
                # if new_mark == 1:
                #     raw_food.likes = raw_food.likes + 1
                #     if feedback_raw_food_modified.mark == 2 or feedback_raw_food_modified.mark == 3:
                #         raw_food.dislikes_no_opinion = raw_food.dislikes_no_opinion - 1
                # elif new_mark == 2 or new_mark == 3:
                #     raw_food.dislikes_no_opinion = raw_food.dislikes_no_opinion + 1
                #     if feedback_raw_food_modified.mark == 1:
                #         raw_food.likes = raw_food.likes - 1
                # elif new_mark == 4:
                #     if feedback_raw_food_modified.mark == 1:
                #         raw_food.likes = raw_food.likes - 1
                #     elif feedback_raw_food_modified.mark == 2 or feedback_raw_food_modified.mark == 3:
                #         raw_food.dislikes_no_opinion = raw_food.dislikes_no_opinion - 1
                # if (raw_food.likes + raw_food.dislikes_no_opinion) > 0:
                #     raw_food.percent = (raw_food.likes / (raw_food.likes + raw_food.dislikes_no_opinion)) * 100
                # else:
                #     raw_food.percent = 0
                # raw_food.save()
                feedback_raw_food_modified.mark = new_mark
                feedback_raw_food_modified.save()
        return redirect('history_tried')

    elif request.method == 'GET':
        return render(
            request,
            'diet_optimizer_website/history_tried.html',
            {'recipes_name' : recipes_name,
            'recipes_link' : recipes_link,
            'marks' : marks,
            'recipes' : recipes,
            'feedbacks' : feedbacks,
            'feedbacks_raw_food' : feedbacks_raw_food,
            'raw_foods' : raw_foods,
            'raw_foods_name' : raw_foods_name})


def most_popular_recipes_foods(request):
    """ view to show the most pupular recipes and foods.

    This view allows the user to see what are the most liked recipes and foods.
    It will simply load the 5 most liked recipes and foods and render the page.
    """
    # recipes and foods are already ordered by popularity. We thus get only the five first of them.
    most_popular_recipes = Recipe.objects.all()[:5]

    # Uncomment if you want to enable food popularity
    # most_popular_foods = USDAfoods.objects.all()[:5]
    # return render(
    #     request,
    #     'diet_optimizer_website/most_popular_recipes_foods.html',
    #     {'most_popular_recipes' : most_popular_recipes,
    #     'most_popular_foods' : most_popular_foods})

    
    return render(
        request,
        'diet_optimizer_website/most_popular_recipes_foods.html',
        {'most_popular_recipes' : most_popular_recipes})


def get_recipe(request):
    """ Get recipe view.

    This view allows the user to enter all the information necessary to search recipes.
    It will first gather all possible data concerning the user's preferences.
    It will then load all the names of the recipes the user liked.

    Finally it will create a form to get recipes and fill it with the user's preferences.
    Finally it will simply render the page.
    """
    user = request.user
    userDB = user.userdb
    userData = UserData(user)

    user_daily_nutrients = userData.daily_nutrients

    # gathering user's favorite cuisines
    favorite_cuisines = PreferenceCuisines.objects.filter(userdb=userDB)
    favorite_cuisines_list = []
    for favorite_cuisine in favorite_cuisines:
        favorite_cuisines_list.append(favorite_cuisine.cuisine_name)

    # gathering user's favorite raw foods
    favorite_raw_foods = PreferenceRawFoods.objects.filter(userdb=userDB)
    favorite_raw_foods_list = []
    for favorite_raw_food in favorite_raw_foods:
        favorite_raw_foods_list.append(favorite_raw_food.raw_food_name)

    # GetRecipeForms has to be created with an userDB to be able to fill the last fields with
    # user's favorite recipes.
    form = GetRecipeForm(userDB,
                        initial={'cuisines': favorite_cuisines_list,
                                  'rawGroups': favorite_raw_foods_list,
                                  'calLow': user_daily_nutrients.get("cal_low"),
                                  'calUp': user_daily_nutrients.get("cal_up"),
                                  'carbLow': user_daily_nutrients.get("carb_low"),
                                  'carbUp': user_daily_nutrients.get("carb_up"),
                                  'protLow': user_daily_nutrients.get("prot_low"),
                                  'protUp': user_daily_nutrients.get("prot_up"),
                                  'fatLow': user_daily_nutrients.get("fat_low"),
                                  'fatUp': user_daily_nutrients.get("fat_up"),
                                  'time': userDB.timeToCook})
    return render(request, "diet_optimizer_website/get_recipe.html",
                        {'user_daily_nutrients': user_daily_nutrients,
                        'form': form,
                        'userDB':userDB})


def save_recipes_in_db(request):
    """Save recipes in d view.

    This view allows the user to select a list of recipes proposed by the website
    and save them so that he can access them later. The recipes are stored by day
    and it is possible to store several days.

    The view will gather the recipes and nutrients in the session data and
    save those information in the database.
    """
    # gathering the recipes the user wants to save.
    diet_recipes = request.session.get('diet_recipes')
    # gathering all the nutrients taken with the recipes the user wants to save.
    total_nutrients_taken = request.session.get('total_nutrients_taken')
    user = request.user
    userDB = user.userdb

    # gathering all the information about the recipes the user wants to save.
    diet_recipes = json.dumps(diet_recipes)
    total_nutrients_taken = json.dumps(total_nutrients_taken)

    # saving the recipes in the database.
    saved_recipes = Saved_Recipes.objects.create(
        user=userDB,
        diet_recipes=diet_recipes,
        total_nutrients_taken=total_nutrients_taken)

    saved_recipes.save()

    return redirect('get_recipe')


def saved_recipes(request):
    """Saved recipes view.

    This view allows the user to see the recipes he has saved. Thus he can have
    acces to the recipes he intended to try at any moment.

    The view will load all the recipes the user saved and their related nutrients.
    It will then load the page with this data.
    """
    user = request.user
    userDB = user.userdb

    # getting all the recipes the user saved.
    all_saved_recipes = Saved_Recipes.objects.filter(user=userDB).all()
    all_saved_recipes_id = []
    all_recipes = []
    all_total_nutrients_taken = []

    for daily_recipes in all_saved_recipes :
        # gathering all the ids of the recipes.
        all_saved_recipes_id.append(daily_recipes.pk)
        # gathering all the information about the saved recipes.
        all_recipes.append(json.loads(daily_recipes.diet_recipes))
        # gathering all the nutrients taken if you take all those recipes.
        all_total_nutrients_taken.append(json.loads(daily_recipes.total_nutrients_taken))

    # giving all the gathered information in a zip (several lists in a single variable)
    all_recipes_nutrients = zip(all_saved_recipes_id, all_recipes, all_total_nutrients_taken)

    # all_recipes_nutrients_filled = list(all_recipes_nutrients)

    return render(
        request,
        'diet_optimizer_website/saved_recipes.html',
        {'all_recipes_nutrients' : all_recipes_nutrients,
        'all_recipes' : all_recipes })


def delete_recipes_in_db(request, pk):
    """"delete recipes in db view.
    
    This view allows the user to delete recipes from his saved recipes whenever he tried them.
    He will be able to have access to it again using the history page.

    :param pk: The primary key of the recipes that should be deleted from the database.

    The view will just load the recipes he selected to delete and remove them from the database.
    """
    user = request.user
    userDB = user.userdb

    delete_recipes = Saved_Recipes.objects.get(id=pk)

    delete_recipes.delete()

    return redirect('saved_recipes')


def get_recipe_confirm(request):
    """ Get recipe confirmation view.

    This view is used to check if the raw foods asked by the user generally corresponds to what he can eat.
    It will first load the user's intolerences and diet.
    It will load the data given in the GetRecipeForm to see what the user asked for.
    If the data is not valid it will redirect the user to get_recipe to ask him to enter data properly.
    However if the data is valid, the view will create a list of every types of foods the user would not want to eat
    according to his diet and intolerences.
    Once this list is done it will check if the foods the user asked for are in this list.
    If any of these foods are asked the view will return the variable launch_popup as true 
    (to say a popup should appear to warn the user)
    It will also return the foods that pose a problem.
    Else it will send launch_popup as false and an empty list.

    :returns: A boolean saying of the user wants to receive popups.
        And a list fo all the groups of foods that pose a problem with the user's search.
    """

    def add_food_pescetarian(impossible_foods):
        """ add food pescetarian view

        :param impossible_foods: List of all the foods that the user can't ask for.

        This function add the impossible kinds of foods for a pescetarian in the impossible_foods set.

        :returns: The list of all the foods the user can't ask for.
        """
        # adding foods pescetarians can't eat to the impossible foods list.
        impossible_foods.add('Lamb, Veal, and Game Products')
        impossible_foods.add('Pork Products')
        impossible_foods.add('Poultry Products')
        impossible_foods.add('Sausages and Luncheon Meats')
        impossible_foods.add('Beef Products')
        return impossible_foods

    def add_food_vegetarian(impossible_foods):
        """ add food pescetarian view

        :param impossible_foods: List of all the foods that the user can't ask for.

        This function add the impossible kinds of foods for a vegetarian in the impossible_foods set.

        :returns: The list of all the foods the user can't ask for.
        """
        # adding foods pescetarians can't eat to the impossible foods list.
        impossible_foods = add_food_pescetarian(impossible_foods)
        # also adding fish to have the list for vegetarians.
        impossible_foods.add('Finfish and Shellfish Products')
        return impossible_foods

    user = request.user
    userDB = user.userdb

    # getting user's intolerences.
    intolerences = Intolerences.objects.filter(userdb=userDB)
    user_intolerences = []
    for intolerence in intolerences:
        user_intolerences.append(intolerence.intolerence_name)

    # getting user's diet.
    user_diet = userDB.diet

    launch_popup = False

    # getting the information about what the user asked for.
    form = GetRecipeForm(userDB,request.GET)

    # checking if the form is vali and creating "cleaned_data"
    if form.is_valid():
        raw_groups = form.cleaned_data.get('rawGroups')
        # creating sets rather than list to avoid having the same foods twice.
        impossible_foods = set()

        # testing every diet and intolerences of the user.
        if 'Dairy' in user_intolerences:
            # Dairy intolerences prohibits dairy
            impossible_foods.add('Dairy and Egg Products')

        if 'Egg' in user_intolerences:
            # Dairy intolerences prohibits eggs
            impossible_foods.add('Dairy and Egg Products')

        if 'Peanut' in user_intolerences or 'Tree Nut' in user_intolerences or 'Sesame' in user_intolerences:
            # Nut and seed products have high chances of containing those foods.
            impossible_foods.add('Nut and Seed Products')

        if 'Seafood' in user_intolerences or 'Shellfish' in user_intolerences:
            # Finfish and Shellfish are prohibited for those intolerences.
            impossible_foods.add('Finfish and Shellfish Products')

        if 'Wheat' in user_intolerences or 'Gluten' in user_intolerences:
            # all those foods have high chance of containing either wheat or gluten.
            impossible_foods.add('Breakfast Cereals')
            impossible_foods.add('Cereal Grains and Pasta')
            impossible_foods.add('Sweets')
            impossible_foods.add('Baked Products')
            if 'Gluten' in user_intolerences:
                # many soups sauces or gravies contains gluten. But few contain Wheat.
                impossible_foods.add('Soups, Sauces, and Gravies')

        if 'Soy' in user_intolerences:
            # Legume Products have high chance of containing Soy.
            impossible_foods.add('Legumes and Legume Products')

        if 'Sulfite' in user_intolerences:
            # Those products have high chances of containing Sulfite.
            impossible_foods.add('Baked Products')
            impossible_foods.add('Soups, Sauces, and Gravies')

        if 'pescetarian' in user_diet:
            impossible_foods = add_food_pescetarian(impossible_foods)

        if 'Vegetarian' in user_diet:
            impossible_foods = add_food_vegetarian(impossible_foods)

        if 'Ovo Vegetarian' in user_diet:
            impossible_foods = add_food_vegetarian(impossible_foods)
            # an ovo vegatarien is a vegetarian that doesn't take dairy products.
            impossible_foods.add('Dairy and Egg Products')

        if 'Vegan' in user_diet or 'Lacto Vegetarian' in user_diet:
            impossible_foods = add_food_vegetarian(impossible_foods)
            impossible_foods.add('Cereal Grains and Pasta')
            impossible_foods.add('Dairy and Egg Products')

        if 'Primal' in user_diet:
            # primal diet prohibits newly found types of foods. 
            impossible_foods.add('Restaurant Foods')
            impossible_foods.add('Breakfast Cereals')
            impossible_foods.add('Cereal Grains and Pasta')
            impossible_foods.add('Nut and Seed Products')
            impossible_foods.add('Sweets')
            impossible_foods.add('Fast Foods')

        if 'Paleo' in user_diet:
            # paleo diet prohibits certain types of foods.
            impossible_foods.add('Dairy and Egg Products')
            impossible_foods.add('Cereal Grains and Pasta')
            impossible_foods.add('Sweets')
            impossible_foods.add('Legumes and Legume Products')
            impossible_foods.add('Fast Foods')
            impossible_foods.add('Breakfast Cereals')
            impossible_foods.add('Nut and Seed Products')


        impossible_foods_selected = []
        for impossible_food in impossible_foods:
            # if the user asked for any food he should not be asking for
            if impossible_food in raw_groups:
                # website has to launch a popup.
                launch_popup = True
                # the following foods are the one he should not ask for.
                impossible_foods_selected.append(impossible_food)

        return(launch_popup,impossible_foods_selected)

    else:
        return (False,["Wrong form"])


def results(request, need_verification):
    """ Results view

    This view will give the user's the results found for his research.

    :param need_verification: A simple integer (0 or 1) telling if the research should be verified(1) or not(0).

    It will start by loading all the user's data. Includng his daily nutrient needs.
    Then it will load the data entered in the GetRecipeForm to know what kind of recipes to search for.
    If this data is not valid it will redirect the user to get recipe to ask him to enter data properly.
    It will then check if the research needs to be verified. If it does it will launch get_recipe_confirm (above)
    If launch popup is true it means some asked foods will be a problem and the view will redirect the user
    on get_recipe to inform him via a popup.
    It will then search in the kinds of food asked if some raw foods correspond to the user's demands and,
    for each of those foods, create a Feedback object for this user.
    Once it has searched for foods it will gather all the necessary information to prepare for the recipe search.
    Additionnaly, if the user asked for a peculiar recipe it will gather it's data first.
    The view will then search all the potential recipes it could use to optimize the search and use those recipes
    to calculate the best set of recipes he could propose to the user.
    For each of those recipes, the view will create a Feedback object for the user.
    Finally it will render the page to show those recipes and foods.
    """
    user = request.user
    userDB = user.userdb
    userData = UserData(user)
    user_daily_nutrients = userData.daily_nutrients

    if request.method == 'GET':
        # GetRecipeForms has to be created with a userDB in it in order for it to fetch all the recipes the user liked.
        # Those froms contain a field with all the recipes liked by the user.
        form = GetRecipeForm(userDB,request.GET)

    # checks if form is properly filled and creates "cleaned_data"
    if not form.is_valid():
        return render(request, 'diet_optimizer_website/get_recipe.html',
                        {'form': form,
                        'user_daily_nutrients': user_daily_nutrients})
    # view contains a need_verification parameter telling if the website should make sure everything the user asked for
    # is in adequation with his diet and intolerences.
    if need_verification=='1':
        launch_popup, impossible_foods_selected = get_recipe_confirm(request)

        # if a popup should be displayed or if the forms was improperly filled:
        if launch_popup or (impossible_foods_selected==["Wrong form"]) :
            # we go back to the template with launch popup set and the list of ingredients that would be agains the user's diet.
            return render(
                request,
                'diet_optimizer_website/get_recipe.html',
                {'form':form,
                'launch_popup':launch_popup,
                'impossible_foods_selected':impossible_foods_selected})


    # gathering all the raw_groups of foods the user asked for.
    raw_groups = form.cleaned_data.get('rawGroups')
    # cleaning the data by removing the + and replacing them with spaces.
    raw_list = [s.replace("+", " ") for s in raw_groups]
    # also cleaning the data by putting / instead of weirdly encoded characters.
    raw_list = [s.replace("%2F", "/") for s in raw_list]
    data = []
    USDAfood_filtered = []
    # for every category of foods the user asked for:
    for raw_food in raw_list:
        # we get all the raw foods of this category
        foods = USDAfoods.objects.filter(group_name=raw_food).all()
        for food in foods:
            # we add all these foods in the list of foods the user could eat.
            USDAfood_filtered.append(food)

    # if we found any foods
    if USDAfood_filtered:
        
        # do twice
        for _ in range(2):
            # getting one of those foods at random and adding it into a list.
            data.append(random.choice(USDAfood_filtered))
        # adding contents of this list into a temporary dictionnary.
        raw_foods_temp = {'raw': [d.__dict__ for d in data]}
    else:
        # if we found no foods, then the temporary dictionnary is empty.
        raw_foods_temp = {}

    # for now the raw foods is an empty list.
    raw_foods = []
    # storing the data in the raw_foods list with the right label for each of the elements of the dictionnary.
    for d in data:
        dct = {
            "NDB_No": d.NDB_No,
            "Desc": d.desc,
            "Cal": d.calorie,
            "Prot": d.protein,
            "Fat": d.fat,
            "Carb": d.carb,
            "Group_Code": d.group_code,
            "Group_Name": d.group_name
        }
        raw_foods.append(dct)

    # calculating the total amount of calories in the raw_foods kept.
    total_raw_calories = sum(item['calorie'] for item in raw_foods_temp['raw'])
    # calculating the total amount of carbs in the raw_foods kept.
    total_raw_carbs = sum(item['carb'] for item in raw_foods_temp['raw'])
    # calculating the total amount of proteins in the raw_foods kept.
    total_raw_protein = sum(item['protein'] for item in raw_foods_temp['raw'])
    # calculating the total amount of fat in the raw_foods kept.
    total_raw_fat = sum(item['fat'] for item in raw_foods_temp['raw'])

    for d in data :
        # we try to get a feedback for this food.
        if FeedbackRawFood.objects.filter(food=d).first():
            # if it exist we inform that it already exists
            print("food already in feedback")
            # if it exists for the current user we also inform it already exists as a feedback.
            if FeedbackRawFood.objects.filter(user=userDB, food=d).first():
                print("user already tried this recipe")
            else:
                # if it doesn't exist we create the feedback.
                temp_feedback_rawfood = FeedbackRawFood(food=d, user=userDB, mark=4, title=d.desc)
                temp_feedback_rawfood.save()
        else:
            # if no feedback exists for this food we create one.
            temp_feedback_rawfood = FeedbackRawFood(food=d, user=userDB, mark=4, title=d.desc)
            temp_feedback_rawfood.save()

    # gathering info about the user.
    # for now we only use the user's first intolerence. No idea why, this could be improved in another version.
    intol = Intolerences.objects.filter(userdb=userDB).first()
    age = UserData(user).age
    cuisine = form.cleaned_data.get('cuisines')
    diet = userDB.diet
    recipe_types = form.cleaned_data.get('recipeTypes')
    objectiveMinMax = form.cleaned_data.get('objectiveMinMax')
    objectiveNutrition = form.cleaned_data.get('objectiveNutrition')
    user_data = UserData(user)

    # storing all this information in the session data. Maybe the django shift made this obsolete.
    # needs investigation in further versions of the code.
    request.session['age'] = age
    request.session['height'] = userDB.height
    request.session['weight'] = userDB.weight
    request.session['gender'] = userDB.gender
    request.session['exercise_level'] = userDB.activity_level
    request.session['diet'] = diet
    request.session['intolerances'] = intol.intolerence_name
    request.session['recipe_types'] = recipe_types
    request.session['obj'] = objectiveMinMax
    request.session['obj_nut'] = objectiveNutrition

    user_daily_nutrients = user_data.daily_nutrients  # without the subtraction of raw foods info

    # gathering user's request concerning the nutrients he should receive.
    carb_low = form.cleaned_data.get('carbLow')
    carb_up = form.cleaned_data.get('carbUp')
    prot_low = form.cleaned_data.get('protLow')
    prot_up = form.cleaned_data.get('protUp')
    fat_low = form.cleaned_data.get('fatLow')
    fat_up = form.cleaned_data.get('fatUp')
    cal_low = form.cleaned_data.get('calLow')
    cal_up = form.cleaned_data.get('calUp')
    time_constraint = form.cleaned_data.get('time')

    # storing these informations in the user_data.daily_nutrients dictionnary.
    if carb_low != '':
        user_data.daily_nutrients['carb_low'] = float(carb_low)
    if carb_up != '':
        user_data.daily_nutrients['carb_up'] = float(carb_up)
    if prot_low != '':
        user_data.daily_nutrients['prot_low'] = float(prot_low)
    if prot_up != '':
        user_data.daily_nutrients['prot_up'] = float(prot_up)
    if fat_low != '':
        user_data.daily_nutrients['fat_low'] = float(fat_low)
    if fat_up != '':
        user_data.daily_nutrients['fat_up'] = float(fat_up)
    if cal_low != '':
        user_data.daily_nutrients['cal_low'] = float(cal_low)
    if cal_up != '':
        user_data.daily_nutrients['cal_up'] = float(cal_up)

    # for recipe calculations. We remove the raw food nutrients from the nutrients the user wanted to take.
    user_daily_nutrients['cal_up'] = user_daily_nutrients['cal_up'] - total_raw_calories
    user_daily_nutrients['carb_up'] = user_daily_nutrients['carb_up'] - total_raw_carbs
    user_daily_nutrients['fat_up'] = user_daily_nutrients['fat_up'] - total_raw_fat

    # handling peculiar recipe asked. If the user wanted a recipe in peculiar the website will provide it in the list.
    asked_recipe = form.cleaned_data.get("peculiar_recipe")
    asked_recipe_nutrients = {}
    # if recipe asked is not "None":
    if asked_recipe != "None":
        # headers necessary for the API request to spoonacular. (SPOONACULAR_KEY is stored in diet_optimizer_conf/settings.py)
        headers = {"X-Mashape-Key": settings.SPOONACULAR_KEY,
                  "Accept": "application/json"}
        # getting the api key of the asked recipe.
        asked_recipe_api = Recipe.objects.filter(title=asked_recipe).first().recipe_id_api
        # loading the spoonacular page of the asked recipe.
        response = requests.get("https://spoonacular-recipe-food-nutrition-v1.p.mashape.com/recipes/" + str(asked_recipe_api) + "/information?includeNutrition=true",
                headers=headers,
                timeout=100)
        # loading the informations in the page into a json format. (dictionnary format)
        response_peculiar_recipe = json.loads(response.text)

        # getting peculiar recipe infos
        peculiar_recipe_time = response_peculiar_recipe.get("readyInMinutes")
        for ob in response_peculiar_recipe.get("nutrition").get("nutrients"):
            if ob.get("title") == 'Calories':
                peculiar_recipe_calories = ob.get("amount")
            if ob.get("title") == 'Carbohydrates':
                peculiar_recipe_carbs = ob.get("amount")
            if ob.get("title") == 'Fat':
                peculiar_recipe_fat = ob.get("amount")
            if ob.get("title") == 'Protein':
                peculiar_recipe_protein = ob.get("amount")
        asked_recipe_nutrients["time"] = peculiar_recipe_time
        asked_recipe_nutrients["calories"] = peculiar_recipe_calories
        asked_recipe_nutrients["carbs"] = peculiar_recipe_carbs
        asked_recipe_nutrients["fat"] = peculiar_recipe_fat
        asked_recipe_nutrients["protein"] = peculiar_recipe_protein
        asked_recipe_nutrients["recipe_ID"] = asked_recipe_api
        asked_recipe_nutrients["pricePerServing"] = response_peculiar_recipe.get("pricePerServing")

    # creating a RecipeHandler object. His objective is to get all the usable recipes for the research done.
    req = RecipeHandler(userDB,user_data.daily_nutrients, cuisine, diet, intol.intolerence_name, "", recipe_types)

    # Asking the RecipeHandler to get the list of all usable recipes for optimization.
    res = req.get_recipes()

    # creating a LinearProgrammingSolver object. It's objective is to use all the available recipes to find
    # the best combination of nutrients considering what the user asked for.
    lp = LinearProgrammingSolver(objectiveMinMax, objectiveNutrition, res['dict_prot'], res['dict_fat'], res['dict_cal'], res['dict_carb'],
                                 res['dict_title'], res['dict_price'], res['dict_time'], res['recipe_types'],
                                 user_data.daily_nutrients, time_constraint, asked_recipe_nutrients)

    # asking the LinearProgrammingSolver object to find the optimal list of recipes.
    lp_func = lp.func_lp()

    # getting the optimal list of recipes (can be empty if no optimal list found.) 
    suggested_recipes = lp_func['suggested_recipes']
    # getting the total number of nutrients taken with all the proposed raw foods and recipes.
    total_nutrients_taken = lp_func['total_nutrients_taken']
    diet_recipes = lp.get_lp_output(suggested_recipes)

    # for every proposed recipe:
    for key in diet_recipes :
        # we search if the recipe exists in the database.
        if Recipe.objects.filter(recipe_id_api=key["id"]).first():
            # if it does exist we get it and check if a feedback for this recipe exists for the user.
            recipe = Recipe.objects.filter(recipe_id_api=key["id"]).first()
            if not(Feedback.objects.filter(user=userDB, recipe=recipe).first()):
                # if it doesn't exists we create the feedback.
                temp_recipes = Recipe.objects.filter(recipe_id_api=key["id"]).first()
                temp_feedback = Feedback.objects.create(recipe=temp_recipes, user=userDB, mark=4, title=temp_recipes.title)
                temp_feedback.save()
        else:
            # if the recipe doesn't exist in the database we create it and store it.
            temp_recipes = Recipe.objects.create(recipe_id_api=key["id"], title=key["title"], link=key["sourceUrl"])
            temp_recipes.save()
            # and we also create a feedback for this recipe for the user.
            temp_feedback = Feedback.objects.create(recipe=temp_recipes, user=userDB, mark=4, title=temp_recipes.title)
            temp_feedback.save()

    # we store the recipes and nutrients in the session data. Investigation is still needed to see if it's
    # useful in django.
    request.session['diet_recipes'] = diet_recipes
    request.session['total_nutrients_taken'] = total_nutrients_taken

    return render(request,'diet_optimizer_website/results.html',
                    {'user_info': {'age': age,
                                    'weight': userDB.weight,
                                    'height': userDB.height,
                                    'gender': userDB.gender,
                                    'exercise_level': userDB.activity_level,
                                    'cuisine': cuisine,
                                    'diet': diet,
                                    'intolerances': intol.intolerence_name,
                                    'obj': objectiveMinMax,
                                    'obj_nut': objectiveNutrition,
                                    'recipe_types': recipe_types,
                                    "raw_groups": raw_groups},
                                    'user_daily_nutrients': user_daily_nutrients,
                                    'recipes': diet_recipes,
                                    'total_nutrients_taken': total_nutrients_taken,
                                    'raw_foods': raw_foods})

