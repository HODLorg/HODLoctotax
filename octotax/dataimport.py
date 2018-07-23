#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pandas as pd


def import_kraken_trades(path='data/raw/', filename='trades.csv'):
    print("Importing trades on Kraken from csv.")
    df_trades = pd.read_csv(path + filename, usecols=["time", "pair", "type", "price", "cost", "fee", "vol"])

    df_trades = df_trades.replace("BCHXBT", "XBCHXXBT")
    df_trades = df_trades.replace("BCHEUR", "XBCHZEUR")
    df_trades = df_trades.replace("EOSEUR", "XEOSZEUR")

    df_trades.to_csv("data/temp/trades.csv")
    print("Import successful.")
