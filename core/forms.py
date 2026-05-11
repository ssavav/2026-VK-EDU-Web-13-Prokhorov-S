from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Profile

class LoginForm(forms.Form):
    username = forms.CharField(label='Login', widget=forms.TextInput(attrs={'class': 'form-control login-area', 'placeholder': 'Enter your login here...'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control login-area', 'placeholder': 'Enter your password here...'}))

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise ValidationError("Incorrect login or password")
            cleaned_data['user'] = user
            
        return cleaned_data

class RegisterForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control login-area', 'placeholder': 'Enter your password here...'}))
    password_confirm = forms.CharField(label='Repeat password', widget=forms.PasswordInput(attrs={'class': 'form-control login-area', 'placeholder': 'Repeat your password here...'}))
    nickname = forms.CharField(label='NickName', required=False, widget=forms.TextInput(attrs={'class': 'form-control login-area', 'placeholder': 'Enter your nickname here...'}))

    class Meta:
        model = User
        fields = ['username', 'email']
        
        labels = {
            'username': 'Username',
            'email': 'Email',
        }
        
        help_texts = {
            'username': '',
        }
        
        error_messages = {
            'username': {
                'unique': "This username is already taken",
            },
            'email': {
                'invalid': "Email is incorrect",
            }
        }
        

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control login-area', 'placeholder': 'Enter your login here...'}),
            'email': forms.EmailInput(attrs={'class': 'form-control login-area', 'placeholder': 'Enter your email here...'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Passwords do not match")

        if password:
            try:
                validate_password(password)
            except ValidationError as e:
                self.add_error('password', e)

        return cleaned_data


    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                nickname=self.cleaned_data.get('nickname', '')
            )
        return user
    

class ProfileSettingsForm(forms.ModelForm):
    nickname = forms.CharField(label='NickName', required=False, widget=forms.TextInput(attrs={'class': 'form-control login-area', 'placeholder': 'Enter your nickname here...'}))
    
    class Meta:
        model = User
        fields = ['username', 'email']

        labels = {
            'username': 'Username',
            'email': 'Email',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control login-area'}),
            'email': forms.EmailInput(attrs={'class': 'form-control login-area'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'profile'):
            self.initial['nickname'] = self.instance.profile.nickname

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            profile = user.profile
            profile.nickname = self.cleaned_data.get('nickname', '')
            profile.save()
        return user