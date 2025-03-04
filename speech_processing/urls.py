from django.urls import path
from .views import practice_words, recognize_word, speech_history, generate_audio

urlpatterns = [
    path('practice/', practice_words, name='practice_words'),
    path('history/', speech_history, name='speech_history'),
    path('recognize/<str:word>/', recognize_word, name='recognize_word'),
    path('audio/<str:word>/', generate_audio, name='generate_audio'),  # ✅ Fix audio URL
]
