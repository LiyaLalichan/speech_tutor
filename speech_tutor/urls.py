from django.contrib import admin
from django.urls import path, include
from accounts.views import home  # ✅ Import home view from accounts

urlpatterns = [
    path('', home, name='home'),  # ✅ Set home() as the homepage
    path('admin/', admin.site.urls),
    path('speech/', include('speech_processing.urls')),
    path('accounts/', include('accounts.urls')),
]
