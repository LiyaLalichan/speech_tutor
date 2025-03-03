from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import RegisterForm
from django.contrib.auth.forms import AuthenticationForm

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Save user object but don't commit yet
            user.set_password(form.cleaned_data['password1'])  # Hash password properly
            user.save()  # Now save the user
            login(request, user)  # Log in the user after signup
            return redirect('home')  # Redirect to homepage after signup
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Redirect after login
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('home')  # Redirect to homepage after logout

from django.shortcuts import render

def home(request):
    return render(request, 'accounts/home.html')
