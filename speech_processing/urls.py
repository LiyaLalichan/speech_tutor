from django.urls import path
from .views import practice_words, recognize_word, get_audio, play_audio  # ✅ Import new view

urlpatterns = [
    path('practice/', practice_words, name='practice_words'),
    path('recognize/<str:word>/', recognize_word, name='recognize_word'),
    path('audio/generate/<str:word>/', get_audio, name='get_audio'),  # ✅ Generate correct audio
    path('audio/play/<str:word>/', play_audio, name='play_audio'),  # ✅ Play correct audio
]
