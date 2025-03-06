from django.contrib import admin
from django.urls import path, include
from speech_processing.views import practice_words  # ✅ Import the practice_words view

urlpatterns = [
    path('', practice_words, name='home'),  # ✅ Set practice_words as the homepage
    path('admin/', admin.site.urls),
    path('speech/', include('speech_processing.urls')),
    path('accounts/', include('accounts.urls')),
]
