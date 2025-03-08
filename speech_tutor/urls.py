# speech_tutor/urls.py
from django.contrib import admin
from django.urls import path, include
from accounts.views import home, register_view
from django.contrib.auth import views as auth_views
from speech_processing import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('accounts/register/', register_view, name='register'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('speech_processing/', include('speech_processing.urls')),
    path('', include('speech_processing.urls')),
    path('speech/recognize/<str:word>/', views.recognize_word, name='recognized_word'),
    # Other URL patterns...views.
]