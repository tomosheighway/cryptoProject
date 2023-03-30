from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from . forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import requests
from django.shortcuts import render
from django.contrib import messages
from users.models import Portfolio 
from decimal import Decimal
import json
from datetime import datetime
from django.http import JsonResponse

def get_bitcoin_price():
    url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=gbp'
    response = requests.get(url).json()
    return response['bitcoin']['gbp']

def get_crypto_prices():
    url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=gbp'
    response = response = requests.get(url).json()
    return response

# https://blockchain.info/rawaddr/{wallet_address}                alternataive endpoint 
def get_bitcoin_balance(wallet_address):
    url = f'https://api.blockcypher.com/v1/btc/main/addrs/{wallet_address}/balance'
    response = requests.get(url).json()
    return response["final_balance"] / 100000000 

    # value in satoshi  convert by div    e.g  = balance / 100000000
# def get_bitcoin_balance():
#     url = 'https://api.blockcypher.com/v1/btc/main/addrs/16ftSEQ4ctQFDtVZiUBusQUjRrGhM3JYwe/balance'
#     # https://blockchain.info/rawaddr/16ftSEQ4ctQFDtVZiUBusQUjRrGhM3JYwe
#     response = requests.get(url).json()
#     print(response) 
#     return response["final_balance"]

def get_ethereum_balance(wallet_address):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_getBalance",
        "params": [wallet_address, "latest"]
    }
    response = requests.post("https://mainnet.infura.io/v3/abf01257db754eb0ac8234697a7a414d", json=payload)
    response.raise_for_status()  # raise an exception if the HTTP request failed
    balance_wei = int(response.json()['result'], 16)
        # convert the balance to Ether
    balance_eth = balance_wei / 10**18
    print(balance_eth)  # print the balance to the console
    return balance_eth
    


def home(request):
    temp_wallet = "16ftSEQ4ctQFDtVZiUBusQUjRrGhM3JYwe"
    bitcoin_price = get_bitcoin_price()
    # bitcoin_balance = get_bitcoin_balance(temp_wallet)
    return render(request, 'users/home.html', {'bitcoin_price': bitcoin_price})
    #return render(request, 'users/home.html', {'bitcoin_price': bitcoin_price, 'bitcoin_balance': bitcoin_balance})


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
    # Set up the API endpoint and parameters
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {
        "vs_currency": "gbp",
        "days": "365",
        "interval": "daily"
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = json.loads(response.content)

        # Extract the trading prices and timestamps from the response
        prices = data['prices']
        timestamps = [datetime.fromtimestamp(timestamp[0]/1000) for timestamp in prices]
        prices_gbp = [price[1] for price in prices]

        # Create a list of dictionaries containing the timestamp and price data
        data_list = [{'x': timestamp, 'y': price} for timestamp, price in zip(timestamps, prices_gbp)]

        # Return the data as a JSON response
        print(data_list)
        return JsonResponse({'data': data_list})
        

    else:
        print(f"Error fetching data: {response.status_code}")


@login_required()
def graphs(request):
    bitcoin_data = bitcoin_chart(request)
    return render(request, 'users/graphs.html')




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
        # bitcoin_price = get_bitcoin_price()
        crypto_prices = get_crypto_prices()
        bitcoin_price = crypto_prices['bitcoin']['gbp']
        ethereum_price = crypto_prices['ethereum']['gbp']


        for portfolio in portfolios:
            if portfolio.currency.lower() == "btc":
                balance = get_bitcoin_balance(portfolio.address)
                portfolio.balance = balance 
                portfolio.value = balance * bitcoin_price
            
            elif portfolio.currency.lower() == "eth":
                balance = get_ethereum_balance(portfolio.address)
                if balance is not None:
                    portfolio.balance = balance
                    portfolio.value = balance * ethereum_price
                else:
                    messages.warning(request, "Failed to get Ethereum balance.")
            else:
                messages.warning(request, f"{portfolio.currency} is not supported.")
        
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
        


