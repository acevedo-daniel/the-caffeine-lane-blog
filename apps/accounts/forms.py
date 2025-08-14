from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


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


class RegistrationStep2Form(UserCreationForm):

    TEXT_INPUT_CLASS = "text-black text-xs font-mont font-light tracking-wide"

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
        )

    def save(self, commit=True, email=None):
        user = super().save(commit=False)
        if email:
            user.email = email

        if commit:
            user.save()
            profile, created = Profile.objects.get_or_create(user=user)
            profile.gender = self.cleaned_data.get("gender")
            profile.has_moto = self.cleaned_data.get("has_moto") == "True"
            profile.save()
        return user


class ProfileForm(forms.ModelForm):

    gender = forms.ChoiceField(
        choices=Profile.GENDER_CHOICES,
        widget=forms.RadioSelect,
        required=False,
        label="What is your gender?",
    )

    has_moto = forms.ChoiceField(
        choices=[(True, "Yes"), (False, "No")],
        widget=forms.RadioSelect,
        label="Do you own a motorcycle?",
    )

    class Meta:
        model = Profile
        fields = ["bio", "avatar", "personal_url", "birth_date", "gender", "has_moto"]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
            "bio": forms.Textarea(attrs={"rows": 3}),
        }
