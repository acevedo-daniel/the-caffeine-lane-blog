from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from .forms import ProfileForm

from .forms import (
    EmailRegistrationForm, 
    CustomRegistrationForm, 
    ProfileForm,
    CustomLoginForm,
    CustomPasswordChangeForm,
    CustomPasswordResetForm
)
from .models import Profile


@never_cache
@require_http_methods(["GET", "POST"])
def register_step1(request):
    """
    Vista para el primer paso del registro: captura del email.
    """
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in.')
        return redirect('home')

    if request.method == 'POST':
        form = EmailRegistrationForm(request.POST)
        if form.is_valid():
            request.session['registration_email'] = form.cleaned_data['email']
            messages.success(request, 'Email verified! Please continue with your registration.')
            return redirect('register_step2')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EmailRegistrationForm()

    context = {
        'form': form,
        'step': 1
    }
    return render(request, 'accounts/register_step1.html', context)


@never_cache
@require_http_methods(["GET", "POST"])
def register_step2(request):
    """
    Vista para el segundo paso del registro: completar información del usuario.
    """
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in.')
        return redirect('home')

    email = request.session.get('registration_email')
    if not email:
        messages.warning(request, 'Please start the registration process from the beginning.')
        return redirect('register_step1')

    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(email=email)
                login(request, user)
                
                # Limpiar la sesión
                if 'registration_email' in request.session:
                    del request.session['registration_email']
                
                messages.success(request, f'Welcome to The Caffeine Lane, {user.first_name}!')
                messages.info(request, 'Your account has been created successfully. You can update your profile anytime.')
                return redirect('home')
                
            except ValidationError as e:
                messages.error(request, f'Registration failed: {e.message}')
            except Exception as e:
                messages.error(request, 'An error occurred during registration. Please try again.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomRegistrationForm()

    context = {
        'form': form,
        'email': email,
        'step': 2
    }
    return render(request, 'accounts/register_step2.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def profile(request):
    """
    Vista para mostrar y editar el perfil del usuario.
    """
    # Obtener o crear el perfil
    profile_obj, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile_obj)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Your profile has been updated successfully!')
                return redirect('profile')
            except Exception as e:
                messages.error(request, f'Error updating profile: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileForm(instance=profile_obj)
        if created:
            messages.info(request, 'Complete your profile to get the most out of The Caffeine Lane.')

    context = {
        'form': form,
        'profile': profile_obj
    }
    return render(request, 'accounts/profile.html', context)


@csrf_protect
@require_http_methods(["GET", "POST"])
def custom_logout(request):
    """
    Vista personalizada para cerrar sesión.
    """
    if request.method == 'POST':
        username = request.user.username if request.user.is_authenticated else None
        logout(request)
        
        if username:
            messages.success(request, f'Goodbye {username}! You have been logged out successfully.')
        else:
            messages.info(request, 'You have been logged out.')
            
        return redirect('home')
    
    # Si es GET, mostrar página de confirmación
    return render(request, 'accounts/logout.html')


# Vista para manejar errores de autenticación
def auth_error(request):
    """
    Vista para manejar errores de autenticación.
    """
    messages.error(request, 'Authentication error. Please try logging in again.')
    return redirect('login')


# Funciones auxiliares para las vistas basadas en clase
def get_success_url_with_message(request, message, redirect_url='home'):
    """
    Función auxiliar para añadir mensaje y redirigir.
    """
    messages.success(request, message)
    return redirect_url

@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'accounts/edit_profile.html', {'form': form})