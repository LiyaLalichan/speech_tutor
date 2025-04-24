from django.urls import path
from accounts.views import user_logout
from .views import (
    practice_words, 
    recognize_word,
    get_word_details,
    generate_audio,
    get_word_meaning
)

urlpatterns = [
    path('practice/', practice_words, name='practice_words'),
    path('recognize/<str:text>/', recognize_word, name='recognize_word'),
    path('get-word-details/<str:text>/', get_word_details, name='get_word_details'),
    path('word-details/<str:word>/', get_word_details, name='word_details'),  # Keeping both word detail paths
    path('audio/generate/<str:word>/', generate_audio, name='get_audio'),
    path('speech/generate-audio/', generate_audio, name='generate_audio'),  # Keeping both audio generation paths
    path("accounts/logout/", user_logout, name="logout"),
]