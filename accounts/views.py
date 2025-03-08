# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.sessions.models import Session

from .forms import CustomUserCreationForm  # Changed from UserRegistrationForm

def home(request):
    return render(request, 'accounts/home.html')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)  # Changed from UserRegistrationForm
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()  # Changed from UserRegistrationForm
    
    return render(request, 'accounts/register.html', {'form': form})

# accounts/views.py
def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        from django.contrib.auth import authenticate
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect("/speech_processing/practice/")
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, "accounts/login.html")

def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect("login")

def logout_all(request):
    Session.objects.all().delete()
    return HttpResponse("All users have been logged out!")