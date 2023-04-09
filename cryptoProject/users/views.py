from django.shortcuts import render, redirect ,get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from . forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import requests
from users.models import Portfolio 
from decimal import Decimal
import json
from datetime import datetime
from django.http import JsonResponse
import re

import requests

def get_crypto_details():
    url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=gbp&ids=bitcoin%2Cethereum&order=market_cap_desc&per_page=5&page=1&sparkline=false&locale=en'
    response = requests.get(url).json()

    result = {}
    for coin in response:
        result[coin['id']] = {
            'current_price': coin['current_price'],
            'market_cap': coin['market_cap'],
            'high_24h': coin['high_24h'],
            'low_24h': coin['low_24h'],
            'price_change_24h': coin['price_change_24h'],
            'price_change_percentage_24h': coin['price_change_percentage_24h']
        }

    return result

def get_crypto_prices():
    url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=gbp'
    response = response = requests.get(url).json()
    return response

# https://blockchain.info/rawaddr/{wallet_address}                alternataive endpoint 
def get_bitcoin_balance(wallet_address):
    if not re.match("^(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}$", wallet_address):
        raise ValueError("Invalid Bitcoin address")
    url = f'https://api.blockcypher.com/v1/btc/main/addrs/{wallet_address}/balance'
    response = requests.get(url).json()
    return response["final_balance"] / 100000000

def get_ethereum_balance(wallet_address):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_getBalance",
        "params": [wallet_address, "latest"]
    }
    response = requests.post("https://mainnet.infura.io/v3/abf01257db754eb0ac8234697a7a414d", json=payload)
    response.raise_for_status()
    balance_wei = int(response.json()['result'], 16)
    balance_eth = balance_wei / 10**18
    return balance_eth
    


def home(request):
    crypto_prices = get_crypto_prices()
    bitcoin_price = crypto_prices['bitcoin']['gbp']
    ethereum_price = crypto_prices['ethereum']['gbp']
    return render(request, 'users/home.html', {'bitcoin_price': bitcoin_price, 'ethereum_price': ethereum_price})
    


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


def bitcoin_chart(request):
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {
        "vs_currency": "gbp",
        "days": "max",
        "interval": "daily"
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = json.loads(response.content)

        prices = data['prices']
        timestamps = [datetime.fromtimestamp(timestamp[0]/1000).strftime('%d/%m/%Y') for timestamp in prices]
        # timestamps = [datetime.fromtimestamp(timestamp[0]/1000).strftime('%d-%m-%Y %H:%M') for timestamp in prices]
        prices_gbp = [price[1] for price in prices]
        data_list = [{'x': timestamp, 'y': price} for timestamp, price in zip(timestamps, prices_gbp)]
        #print({'data': data_list})
        return JsonResponse({'data': data_list})
        

    else:
        print(f"Error fetching data: {response.status_code}")

def ethereum_chart(request): 
    url = "https://api.coingecko.com/api/v3/coins/ethereum/market_chart"
    params = {
        "vs_currency": "gbp",
        "days": "max",
        "interval": "daily"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = json.loads(response.content)
        prices = data['prices']
        timestamps = [datetime.fromtimestamp(timestamp[0]/1000).strftime('%d/%m/%Y') for timestamp in prices]
        prices_gbp = [price[1] for price in prices]
        data_list = [{'x': timestamp, 'y': price} for timestamp, price in zip(timestamps, prices_gbp)]
        # print({'data': data_list})
        return JsonResponse({'data': data_list})
    else:
        print(f"Error fetching data: {response.status_code}")

def is_valid_btc_address(wallet_address):
    if re.match("^(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}$", wallet_address):
        return True
    else:
        return False

def is_valid_eth_address(wallet_address):
    if re.match("^0x[a-fA-F0-9]{40}$", wallet_address):
        return True
    else:
        return False


@login_required()
def graphs(request):
    crypto_stats = get_crypto_details()
    bitcoin_data = bitcoin_chart(request)
    ethereum_data = ethereum_chart(request)
    return render(request, 'users/graphs.html' , {'bitcoin_data': bitcoin_data, 'ethereum_data': ethereum_data, 'crypto_stats': crypto_stats})


@login_required()
def portfolio(request):
    if request.method == 'POST':
        wallet_address = request.POST.get('wallet_address')
        currency_name = request.POST.get('currency_name')

        if Portfolio.objects.filter(user=request.user, address=wallet_address, currency=currency_name).exists():
            messages.warning(request, f"The wallet address {wallet_address} already exists in your portfolio.")
            return redirect('portfolio')

        if currency_name.lower() == 'btc':
            if not is_valid_btc_address(wallet_address):
                messages.warning(request, 'Invalid Bitcoin wallet address.')
                return redirect('portfolio')
        elif currency_name.lower() == 'eth':
            if not is_valid_eth_address(wallet_address):
                messages.warning(request, 'Invalid Ethereum wallet address.')
                return redirect('portfolio')
        else:
            messages.warning(request, 'Invalid currency selected.')
            return redirect('portfolio')

        portfolio = Portfolio.objects.create(user=request.user, address=wallet_address, currency=currency_name)
        messages.success(request, 'Crypto wallet added successfully!')
        print("Created successfully")
        return redirect('portfolio')
    else:
        portfolios = Portfolio.objects.filter(user=request.user)
        crypto_prices = get_crypto_prices()
        bitcoin_price = crypto_prices['bitcoin']['gbp']
        ethereum_price = crypto_prices['ethereum']['gbp']
        total_value = 0

        for portfolio in portfolios:
            if portfolio.currency.lower() == 'btc':
                if is_valid_btc_address(portfolio.address):
                    balance = get_bitcoin_balance(portfolio.address)
                    portfolio.balance = balance 
                    portfolio.value = round(balance * bitcoin_price, 2)
                    
                else:
                    messages.warning(request, 'A invalid Bitcoin wallet address has been found in your portfolio.')
            elif portfolio.currency.lower() == 'eth':
                if is_valid_eth_address(portfolio.address):
                    balance = get_ethereum_balance(portfolio.address)
                    if balance is not None:
                        portfolio.balance = balance
                        portfolio.value = round(balance * ethereum_price, 2)
                    else:
                        messages.warning(request, 'Failed to get Ethereum balance.')
                else:
                    messages.warning(request, 'A invalid Ethereum wallet address found in your  portfolio.')
            else:
                messages.warning(request, f"{portfolio.currency} is not supported.")
            
            total_value += portfolio.value
            #print("total" , total_value)

        return render(request, 'users/portfolio.html', {'portfolios': portfolios, 'total_value': total_value})

def delete_portfolio(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
    if request.method == 'POST':
        portfolio.delete()
        messages.success(request, 'A wallet address has been deleted ')
        return redirect('portfolio')
    return render(request, 'users/delete_portfolio.html', {'portfolio': portfolio})


@login_required
def delete_account(request):
    if request.method == 'POST':
        request.user.delete() 
        messages.success(request, 'Your account has been deleted.')
        return redirect('home')
    else:
        return render(request, 'users/delete_user.html')

@login_required
def delete_user(request):
    return render(request, 'users/delete_user.html')
