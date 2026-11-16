from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Project, User


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'autofocus': True}))

    def clean_username(self):
        return self.cleaned_data['username'].strip().lower()


class RegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email']
        labels = {'username': 'Display name'}

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account already uses this email address.')
        return email


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description']
        labels = {'name': 'Group or project name'}


class JoinGroupForm(forms.Form):
    code = forms.UUIDField(label='Group code')
