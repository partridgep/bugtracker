from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Project, Bug


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required')

    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2', )

class BugForm(ModelForm):
    class Meta:
        model = Bug
        fields = '__all__'
