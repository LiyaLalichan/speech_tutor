from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
# Replace 'accounts' with the actual app name where CustomUser is defined
from accounts.models import CustomUser

# Register the User model
admin.site.register(CustomUser, UserAdmin)