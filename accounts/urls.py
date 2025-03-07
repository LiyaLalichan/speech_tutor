from django.urls import path
from . import views
from speech_processing.views import practice_words 
from .views import register, user_login, user_logout, home # Add home here

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", user_login, name="login"),
     path('speech-processing/', practice_words, name='speech_recognition'),
    path("logout/", user_logout, name="logout"),
    path("home/", home, name="home"),  # Add this line
]