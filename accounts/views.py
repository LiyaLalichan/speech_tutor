from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm  # ✅ Import the missing form
from .forms import CustomUserCreationForm

def home(request):
    return render(request, 'accounts/home.html')  # ✅ Load the new UI from accounts


# ✅ Register a User
def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # ✅ Log in the user after registration
            return redirect("home")  # ✅ Redirect to home page
    else:
        form = CustomUserCreationForm()
    return render(request, "accounts/register.html", {"form": form})

# ✅ Login View
def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("/speech/practice/")  # ✅ Redirect to home page after login
    else:
        form = AuthenticationForm()
    return render(request, "accounts/login.html", {"form": form})

# ✅ Logout View
def user_logout(request):
    logout(request)
    return redirect("login")  # ✅ Redirect to login page after logout
