from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    dob = models.DateField(null=True, blank=True)  # Date of Birth
    phone = models.CharField(max_length=10, null=True, blank=True)  # Phone Number

    class Meta:
        swappable = 'AUTH_USER_MODEL'
