#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import time
import json
import requests


def get_price_history(base_currency="BTC", quote_currency="EUR"):
    filename = "data/history/price_{}_{}.json".format(base_currency, quote_currency)
    price_history = {}
    try:
        if os.path.isfile(filename):
            with open(filename, 'r') as f:
                price_history = json.load(f)
    except Exception:
        pass

    return price_history


def write_historic_price(timestamp, price, base_currency="btc", quote_currency="EUR"):
    filename = "data/history/price_{}_{}.json".format(base_currency, quote_currency)
    price_history = {}

    try:
        if os.path.isfile(filename):
            with open(filename, 'r') as f:
                price_history = json.load(f)
    except Exception:
        pass

    if timestamp not in price_history:
        price_history.update({
            timestamp: price
        })

    try:
        with open(filename, 'w') as f:
            json.dump(price_history, f)
    except Exception:
        pass


def get_price(base_currency="BTC", quote_currency="EUR", timestamp=0, exchange="Kraken"):
    currency_symbols = {
        'XBT': "BTC",
        'XDG': "DOGE"
    }
    if base_currency in currency_symbols:
        base_currency = currency_symbols[base_currency]
    if quote_currency in currency_symbols:
        quote_currency = currency_symbols[quote_currency]

    if timestamp:
        price_history = get_price_history(base_currency, quote_currency)
        price = price_history.get(str(timestamp), None)
        if price:
            return price

        api_endpoint = "https://min-api.cryptocompare.com/data/pricehistorical"
        payload = {
            'fsym': base_currency,
            'tsyms': quote_currency,
            'ts': timestamp,
            'e': exchange
        }
    else:
        api_endpoint = "https://min-api.cryptocompare.com/data/price"
        payload = {
            'fsym': base_currency,
            'tsyms': quote_currency,
            'e': exchange
        }

    response = requests.get(api_endpoint, params=payload)
    data = response.json()

    if "Message" in data:
        if "market does not exist" in data['Message']:
            price_base_currency_xbt = get_price(base_currency, "XBT")
            price_xbt_eur = get_price("XBT", "EUR")
            price = price_base_currency_xbt * price_xbt_eur
            data = {
                base_currency: {
                    'EUR': price
                }
            }

    if timestamp:
        price = data[base_currency][quote_currency]
    else:
        price = data[quote_currency]
        timestamp = int(time.time())

    write_historic_price(timestamp, price, base_currency, quote_currency)

    return price
