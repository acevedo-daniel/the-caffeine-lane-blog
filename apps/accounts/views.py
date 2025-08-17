from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect

from .forms import EmailRegistrationForm, ProfileForm, RegistrationStep2Form
from .models import Profile


def register_step1(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = EmailRegistrationForm(request.POST)
        if form.is_valid():
            request.session["registration_email"] = form.cleaned_data["email"]
            return redirect("register_step2")
    else:
        form = EmailRegistrationForm()

    return render(request, "accounts/register_step1.html", {"form": form})


def register_step2(request):
    if request.user.is_authenticated:
        return redirect("home")

    email = request.session.get("registration_email")
    if not email:
        return redirect("register_step1")

    if request.method == "POST":
        form = RegistrationStep2Form(request.POST)
        if form.is_valid():
            user = form.save(email=email)
            login(request, user)
            del request.session["registration_email"]
            messages.success(request, "Account successfully created!")
            messages.info(
                request,
                "Welcome! Please visit your profile page to add your name and other details.",
            )
            return redirect("home")
    else:
        form = RegistrationStep2Form()

    return render(request, "accounts/register_step2.html", {"form": form})


@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile successfully updated!")
            return redirect("profile")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProfileForm(instance=profile)

    return render(request, "accounts/profile.html", {"form": form})


@csrf_protect
def custom_logout(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "You have successfully logged out!")
        return redirect("home")

    return render(request, "accounts/logout.html")
