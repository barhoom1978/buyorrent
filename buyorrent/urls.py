from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('input', views.input, name='input'),
    path('do_financial_calcs', views.do_financial_calcs, name='do_financial_calcs'),
    path('user_profile', views.user_profile, name='user_profile'),
    path('delete_scenario', views.delete_scenario, name='delete_scenario'),

    path('login', views.login_page, name='login'),
    path('logout', views.logout_page, name='logout'),
    path('register', views.register, name='register'),
    ]
