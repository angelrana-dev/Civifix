from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Issue


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ["title", "category", "description", "photo", "address", "latitude", "longitude"]
        widgets = {"description": forms.Textarea(attrs={"rows": 4}),
                   "latitude": forms.HiddenInput(), "longitude": forms.HiddenInput()}


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="You can log in with your email or username.")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists. Log in instead.")
        return email


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username or email", widget=forms.TextInput(attrs={"autofocus": True}))