from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import (
    CustomLoginForm, 
    CustomPasswordChangeForm, 
    CustomPasswordResetForm, 
    CustomSetPasswordForm
)

# Configuración personalizada para las vistas de autenticación
class CustomLoginView(auth_views.LoginView):
    form_class = CustomLoginForm
    template_name = 'accounts/login.html'
    
    def get_success_url(self):
        return self.get_redirect_url() or '/home/'


class CustomPasswordChangeView(auth_views.PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'accounts/password_change.html'
    success_url = '/accounts/password_change_done/'


class CustomPasswordResetView(auth_views.PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = '/accounts/password_reset_done/'


class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'accounts/password_reset_confirm.html'
    success_url = '/accounts/password_reset_complete/'


urlpatterns = [
    # Registro
    path('register/step1/', views.register_step1, name='register_step1'),
    path('register/step2/', views.register_step2, name='register_step2'),
    path('register/', views.register_step1, name='register'),  # Alias para compatibilidad
    
    # Autenticación
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    
    # Perfil
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # Cambio de contraseña
    path('password_change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change_done/', 
         auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), 
         name='password_change_done'),
    
    # Reset de contraseña
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset_done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), 
         name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', 
         CustomPasswordResetConfirmView.as_view(), 
         name='password_reset_confirm'),
    path('password_reset_complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), 
         name='password_reset_complete'),
    
    # Error handling
    path('auth_error/', views.auth_error, name='auth_error'),
]