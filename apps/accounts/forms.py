from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


# --- Este formulario permanece igual ---
class EmailRegistrationForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"placeholder": "Your email address"}),
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "A user with that email already exists. Please choose a different one."
            )
        return email


# --- Formulario de Paso 2 (Refactorizado) ---
class RegistrationStep2Form(UserCreationForm):
    """
    Formulario refactorizado para definir los estilos y placeholders
    directamente en los widgets, siguiendo las mejores prácticas de Django.
    """

    # Define una clase CSS común para reutilizarla
    TEXT_INPUT_CLASS = "text-black text-xs font-mont font-light tracking-wide"

    # Sobrescribe los campos heredados para añadir widgets personalizados
    username = forms.CharField(
        label="What is your Username?",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": TEXT_INPUT_CLASS,
                "autocomplete": "off",
            }
        ),
    )
    password1 = forms.CharField(
        label="Enter a Password",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": TEXT_INPUT_CLASS,
                "autocomplete": "new-password",
            }
        ),
    )
    password2 = forms.CharField(
        label="Confirm your Password",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirm Password",
                "class": TEXT_INPUT_CLASS,
                "autocomplete": "new-password",
            }
        ),
    )

    # Define los campos personalizados con sus widgets
    first_name = forms.CharField(
        label="First Name",
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "First Name", "class": TEXT_INPUT_CLASS}
        ),
    )
    last_name = forms.CharField(
        label="Last Name",
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "Last Name", "class": TEXT_INPUT_CLASS}
        ),
    )

    # Campos de opciones (Radio buttons)
    gender = forms.ChoiceField(
        choices=[("M", "Male"), ("F", "Female")],
        required=False,
        widget=forms.RadioSelect,
        label="What is your gender?",
    )
    has_moto = forms.ChoiceField(
        choices=[("True", "Yes"), ("False", "No")],
        required=True,
        widget=forms.RadioSelect,
        label="Own a motorcycle?",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
        )  # password1 y password2 son manejados por UserCreationForm

    def save(self, commit=True, email=None):
        # El método save de la clase padre ahora maneja first_name y last_name
        user = super().save(commit=False)
        if email:
            user.email = email

        if commit:
            user.save()
            # Crear o actualizar el perfil asociado
            profile, created = Profile.objects.get_or_create(user=user)
            profile.gender = self.cleaned_data.get("gender")
            # Convertir la cadena 'True'/'False' a booleano para el modelo
            profile.has_moto = self.cleaned_data.get("has_moto") == "True"
            profile.save()
        return user


# --- Este formulario permanece igual ---
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["bio", "avatar", "personal_url", "birth_date", "gender", "has_moto"]
        widgets = {"birth_date": forms.DateInput(attrs={"type": "date"})}
