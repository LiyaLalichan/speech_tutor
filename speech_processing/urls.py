from django.urls import path
from accounts.views import user_logout
from .views import practice_words, recognize_word,get_word_details,generate_audio  # ✅ Import new view

urlpatterns = [
    path('practice/', practice_words, name='practice_words'),
    path('recognize/<str:word>/', recognize_word, name='recognize_word'),
    path('audio/generate/<str:word>/', generate_audio, name='get_audio'),  # ✅ Generate correct audio
    # path('audio/play/<str:word>/', play_audio, name='play_audio'),  # ✅ Play correct audio
    path("accounts/logout/", user_logout, name="logout"),
    path('word-details/<str:word>/', get_word_details, name='word_details'),
    
]
