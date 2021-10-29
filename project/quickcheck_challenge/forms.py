from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import fields
from .models import User


class UserRegisterForm(UserCreationForm):

    class Meta:

        model = User
        fields = ["username", "password1", "password2"]



class LoginForm(forms.Form):

    username = forms.CharField(max_length=255, widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())

