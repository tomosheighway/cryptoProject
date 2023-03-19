from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from . forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import requests

def get_bitcoin_price():
    url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=gbp'
    response = requests.get(url).json()
    return response['bitcoin']['gbp']

def get_bitcoin_balance():
    url = 'https://blockchain.info/rawaddr/16ftSEQ4ctQFDtVZiUBusQUjRrGhM3JYwe'
    response = requests.get(url).json()
    return response["final_balance"]


def home(request):
    bitcoin_price = get_bitcoin_price()
    bitcoin_balance = get_bitcoin_balance()
    return render(request, 'users/home.html', {'bitcoin_price': bitcoin_price, 'bitcoin_balance': bitcoin_balance})


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username= form.cleaned_data.get('username')
            messages.success(request, f'Hi {username} , your account has been created please now login below ' )
            return redirect('login')
    else: 
        form = UserRegisterForm()

    return render(request, 'users/register.html' , {'form':form})

@login_required()
def profile(request):
    return render(request, 'users/profile.html')
