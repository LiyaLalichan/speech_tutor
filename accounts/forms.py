from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    dob = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    phone = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'pattern': '[0-9]{10}'}))

    class Meta:
        model = CustomUser
        fields = ["username", "dob", "email", "phone", "password1", "password2"]
