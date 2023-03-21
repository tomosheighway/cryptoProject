from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    #bitcoin_address = forms.CharField(max_length=50, help_text='Enter your Bitcoin address.')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        # fields = ['username', 'email', 'password1', 'password2' , 'bitcoin_address']


