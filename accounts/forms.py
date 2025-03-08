from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import CustomUser
import re

class CustomUserCreationForm(UserCreationForm):
    name = forms.CharField(max_length=100, required=True)
    dob = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=10, required=True)
    
    class Meta:
        model = CustomUser
        fields = ['name', 'username', 'email', 'dob', 'phone', 'password1', 'password2']
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit():
            raise ValidationError("Phone number should contain only digits.")
        if len(phone) != 10:
            raise ValidationError("Phone number must be 10 digits long.")
        return phone
    
    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if len(password) < 6:
            raise ValidationError("Password must be at least 6 characters long.")
        if not any(char.isupper() for char in password):
            raise ValidationError("Password must contain at least one uppercase letter.")
        if not any(char.isdigit() for char in password):
            raise ValidationError("Password must contain at least one number.")
        return password
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['name']
        user.dob = self.cleaned_data['dob']
        user.phone = self.cleaned_data['phone']
        
        if commit:
            user.save()
        return user