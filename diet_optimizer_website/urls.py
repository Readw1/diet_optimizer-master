from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.conf.urls import url, include
from . import views

urlpatterns = [
    url('^', include('django.contrib.auth.urls')),
    url(r'^home$', views.home, name='home'),
    url(r'^index$', views.index, name='index'),
    url(r'^diet_optimizer_website/signup$', views.signup, name='signup'),
    url(r'^diet_optimizer_website/personal_details$', views.personal_details, name='personal_details'),
    url(r'^diet_optimizer_website/about$', views.about, name='about'),
    url(r'^diet_optimizer_website/logout$', login_required(views.logout_view), name='logout'),
    url(r'^diet_optimizer_website/profile$', login_required(views.profile), name='profile'),
    url(r'^diet_optimizer_website/personal_settings$', login_required(views.personal_settings), name='personal_settings'),
    url(r'^diet_optimizer_website/get_recipe$', login_required(views.get_recipe), name='get_recipe'),
    url(r'^diet_optimizer_website/save_recipes_in_db$', login_required(views.save_recipes_in_db), name='save_recipes_in_db'),
    url(r'^diet_optimizer_website/saved_recipes$', login_required(views.saved_recipes), name='saved_recipes'),
    url(r'^diet_optimizer_website/delete_recipes_in_db/(?P<pk>[0-9]+)$', login_required(views.delete_recipes_in_db), name='delete_recipes_in_db'),
    url(r'^diet_optimizer_website/get_recipe_confirm$', login_required(views.get_recipe_confirm), name='get_recipe_confirm'),
    url(r'^diet_optimizer_website/history_not_tried$', login_required(views.history_not_tried), name='history_not_tried'),
    url(r'^diet_optimizer_website/history_tried$', login_required(views.history_tried), name='history_tried'),
    url(r'^diet_optimizer_website/account_settings$', login_required(views.account_settings), name='account_settings'),
    url(r'^diet_optimizer_website/results/(?P<need_verification>[0-1])$', login_required(views.results), name='results'),
    url(r'^diet_optimizer_website/user_profile$', login_required(views.user_profile), name='user_profile'),
    url(r'^diet_optimizer_website/most_popular_recipes_foods$', login_required(views.most_popular_recipes_foods), name = 'most_popular_recipes_foods'),
    url(r'^diet_optimizer_website/about_logged_in$', login_required(views.about_logged_in), name='about_logged_in'),
    # url(r'^test$', views.test, name='test'),
]
