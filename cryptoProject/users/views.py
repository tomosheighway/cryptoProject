from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from . forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import requests
from django.shortcuts import render
from django.contrib import messages
from users.models import Portfolio 

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
            print(request.POST) 
            username= form.cleaned_data.get('username')
            messages.success(request, f'Hi {username} , your account has been created please now login below ' )
            return redirect('login')
    else: 
        form = UserRegisterForm()

    return render(request, 'users/register.html' , {'form':form})

@login_required()
def profile(request):
    return render(request, 'users/profile.html')

@login_required()
def portfolio(request):
    if request.method == 'POST':
        wallet_address = request.POST.get('wallet_address')
        currency_name = request.POST.get('currency_name')
        portfolio = Portfolio.objects.create(user=request.user, address=wallet_address, currency=currency_name)
        messages.success(request, 'Crypto wallet added successfully!')
        print("Created succesfully")
        return redirect('portfolio')
    else:
        portfolios = Portfolio.objects.filter(user=request.user)
        
    return render(request, 'users/portfolio.html', {'portfolios': portfolios})

    # if request.method == 'POST':
    #     # Handle form submission
    #     currency = request.POST.get('currency_name')
    #     wallet_address = request.POST.get('btc_address')

    #     if currency:
    #         Portfolio.object.create(user=request.user , currency=currency , address=wallet_address)
    #         print("data saved")
            

    # else:
    #     print("oops")
    #     # portfolio_objs =  Portfolio.object.filter(user=request.user)
    #     # wallet_list =[]
        


