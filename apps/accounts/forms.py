from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
import re

from .models import Profile


class EmailRegistrationForm(forms.Form):
    """Formulario para capturar email en el paso 1 del registro"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "register-input register-input-with-icon",
            "placeholder": "Enter your email address",
            "autocomplete": "email"
        }),
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError(
                "A user with that email already exists. Please choose a different one."
            )
        return email


class CustomRegistrationForm(UserCreationForm):
    """Formulario completo de registro (paso 2) con validaciones mejoradas"""

    # Clase CSS común para inputs
    INPUT_CLASS = "register-input" 

    username = forms.CharField(
        label="What is your Username?",
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "class": INPUT_CLASS,
                "placeholder": "Username",
                "autocomplete": "username",
            }
        ),
    )
    
    password1 = forms.CharField(
        label="Enter a Password",
        widget=forms.PasswordInput(
            attrs={
                "class": INPUT_CLASS, 
                "placeholder": "Password",
                "autocomplete": "new-password",
            }
        ),
    )
    
    password2 = forms.CharField(
        label="Confirm your Password",
        widget=forms.PasswordInput(
            attrs={
                "class": INPUT_CLASS, 
                "placeholder": "Confirm Password",
                "autocomplete": "new-password",
            }
        ),
    )
    
    first_name = forms.CharField(
        label="First Name",
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": INPUT_CLASS, 
                "placeholder": "First Name",
                "autocomplete": "given-name"
            }
        ),
    )
    
    last_name = forms.CharField(
        label="Last Name",
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": INPUT_CLASS, 
                "placeholder": "Last Name",
                "autocomplete": "family-name"
            }
        ),
    )
    
    gender = forms.ChoiceField(
        choices=[("M", "Male"), ("F", "Female"), ("O", "Other")], 
        required=False,
        widget=forms.RadioSelect(attrs={"class": "radio-input"}), 
        label="What is your gender?",
    )
    
    has_moto = forms.ChoiceField(
        choices=[("True", "Yes"), ("False", "No")],
        required=True,
        widget=forms.RadioSelect(attrs={"class": "radio-input"}), 
        label="Own a motorcycle?",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name") 

    # Métodos clean personalizados para validación
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if not re.match("^[a-zA-Z0-9_]+$", username):
            raise ValidationError("Username can only contain letters, numbers, and underscores.")
        return username

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        if not re.match("^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", first_name):
            raise ValidationError("First name can only contain letters and spaces.")
        return first_name.strip().title()

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")
        if not re.match("^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", last_name):
            raise ValidationError("Last name can only contain letters and spaces.")
        return last_name.strip().title()

    def save(self, commit=True, email=None):
        user = super().save(commit=False)
        if email:
            user.email = email

        if commit:
            user.save()
            # Crear o actualizar el perfil asociado
            profile, created = Profile.objects.get_or_create(user=user)
            profile.gender = self.cleaned_data.get("gender") or "" 
            profile.has_moto = self.cleaned_data.get("has_moto") == "True" 
            profile.save()
        return user


class CustomLoginForm(AuthenticationForm):
    """Formulario de login personalizado"""
    
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "auth-input",
                "placeholder": "Username or Email",
                "autocomplete": "username"
            }
        )
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "auth-input",
                "placeholder": "Password",
                "autocomplete": "current-password"
            }
        )
    )


class CustomPasswordChangeForm(PasswordChangeForm):
    """Formulario personalizado para cambio de contraseña"""
    
    old_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "auth-input",
                "placeholder": "Current Password",
                "autocomplete": "current-password"
            }
        )
    )
    
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "auth-input",
                "placeholder": "New Password",
                "autocomplete": "new-password"
            }
        )
    )
    
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "auth-input",
                "placeholder": "Confirm New Password",
                "autocomplete": "new-password"
            }
        )
    )


class CustomPasswordResetForm(PasswordResetForm):
    """Formulario personalizado para reset de contraseña"""
    
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(
            attrs={
                "class": "auth-input",
                "placeholder": "Enter your email address",
                "autocomplete": "email"
            }
        )
    )


class CustomSetPasswordForm(SetPasswordForm):
    """Formulario para establecer nueva contraseña después del reset"""
    
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "auth-input",
                "placeholder": "New Password",
                "autocomplete": "new-password"
            }
        )
    )
    
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "auth-input",
                "placeholder": "Confirm New Password",
                "autocomplete": "new-password"
            }
        )
    )


class ProfileForm(forms.ModelForm):
    """Formulario para editar el perfil del usuario"""
    
    class Meta:
        model = Profile
        fields = ["bio", "avatar", "personal_url", "birth_date", "gender", "has_moto"]
        widgets = {
            "bio": forms.Textarea(attrs={
                "class": "profile-field",
                "rows": 4,
                "placeholder": "Tell us about yourself and your riding passion...",
                "maxlength": 500
            }),
            "avatar": forms.FileInput(attrs={
                "class": "profile-field",
                "accept": "image/*"
            }),
            "personal_url": forms.URLInput(attrs={
                "class": "profile-field",
                "placeholder": "https://your-website.com"
            }),
            "birth_date": forms.DateInput(attrs={
                "class": "profile-field",
                "type": "date"
            }),
            "gender": forms.Select(attrs={
                "class": "profile-field"
            }),
            "has_moto": forms.Select(attrs={
                "class": "profile-field"
            })
        }
        labels = {
            "bio": "Bio",
            "avatar": "Avatar",
            "personal_url": "Personal URL",
            "birth_date": "Birth Date",
            "gender": "Gender",
            "has_moto": "Do you have a motorcycle?"
        }

    def clean_bio(self):
        bio = self.cleaned_data.get("bio")
        if bio and len(bio) > 500:
            raise ValidationError("Bio cannot exceed 500 characters.")
        return bio

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            if isinstance(avatar, UploadedFile):
                content_type = avatar.content_type
                if content_type not in ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']:
                    raise ValidationError('Solo se permiten imágenes en formato JPG, PNG o GIF.')
            
            if avatar.size > 5 * 1024 * 1024:
                raise ValidationError('La imagen no puede superar los 5MB.')

        return avatar
