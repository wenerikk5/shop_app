from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views


urlpatterns = [
     # path('login/', auth_views.LoginView.as_view(), name='login'),
     path('login/', views.user_login, name='login'),

     path('logout/', auth_views.LogoutView.as_view(), name='logout'),
     path('register/', views.register, name='register'),

]
