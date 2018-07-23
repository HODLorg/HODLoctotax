#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pandas as pd

from datetime import datetime

from .market import get_price
from .utils import conprint, conexport


FIAT_CURRENCIES = ["USD", "EUR", "JPY", "GBP", "CAD"]


class Taxy:
    def __init__(self, args, path="data/temp/trades.csv"):
        self.args = args

        self.trades = pd.read_csv(path)

        self.ledger = {}
        self.events = {}
        self.total_profit_dfc = 0.0
        self.total_taxes_dfc = 0.0

        self.create_ledger()

    def create_ledger(self):
        # Retrieve unique trading pairs and create placeholders in the ledger
        pairs = self.trades.pair.unique()
        for pair in pairs:
            base_currency = pair[1:4]
            quote_currency = pair[-3:]
            self.ledger.update({
                base_currency: {},
                quote_currency: {}
            })

        # Fill the ledger with existing trades
        for i, trade in sorted(self.trades.iterrows()):
            trade_time = trade.time
            trade_datetime = datetime.strptime(trade_time, "%Y-%m-%d %H:%M:%S.%f")
            trade_timestamp = int(trade_datetime.timestamp())

            trade_type = trade.type
            trade_pair = trade.pair
            trade_base_currency = trade_pair[1:4]
            trade_quote_currency = trade_pair[-3:]
            trade_price = trade.price
            trade_volume = trade.vol
            trade_cost = trade.cost

            if trade_type == "buy":
                change_base_currency = trade_volume
                change_quote_currency = -trade_cost
            elif trade_type == "sell":
                change_base_currency = -trade_volume
                change_quote_currency = trade_cost
            else:
                raise Exception

            # Write value tuple to timestamp key
            self.ledger[trade_base_currency][trade_timestamp] = {
                'timestamp': trade_timestamp,
                'type': trade_type,
                'pair': trade_pair,
                'change': change_base_currency,
                'price': trade_price
            }
            self.ledger[trade_quote_currency][trade_timestamp] = {
                'timestamp': trade_timestamp,
                'type': trade_type,
                'pair': trade_pair,
                'change': change_quote_currency,
                'price': trade_price
            }

    def calculate_fees(self):
        print("\n"
              "# Calculating fees\n"
              "##################")

        total_fees = {}
        for index, trade in self.trades.iterrows():
            quote_currency = trade.pair[-3:]
            if quote_currency not in total_fees:
                total_fees[quote_currency] = trade.fee
            else:
                total_fees[quote_currency] += trade.fee

        price_xbt_dfc = get_price("XBT", "EUR")
        fees_dfc = total_fees['EUR']
        fees_xbt = total_fees['XBT']
        fees_xbt_dfc = fees_xbt * price_xbt_dfc
        total_fees_dfc = fees_dfc + fees_xbt_dfc
        print("Fees:\n"
              "\tEUR: {:.2f} EUR\n"
              "\tXBT: {:.6f} BTC ({:.2f} EUR @ {:.2f} EUR/BTC)\n"
              "\n=> Total fees: {:.2f} EUR\n"
              .format(fees_dfc, fees_xbt, fees_xbt_dfc, price_xbt_dfc, total_fees_dfc))

    def calculate_profit(self):
        print("\n"
              "# Calculating profit\n"
              "####################\n"
              "Method: {}".format(self.args.method))
        conexport(self.args, True,
                  "# Calculation of Profits"
                  "\nMethod: {}".format(self.args.method))

        # Cycle through trades, find sells and calculate profits
        for i, trade in sorted(self.trades.iterrows()):
            trade_time = trade.time
            trade_datetime = datetime.strptime(trade_time, "%Y-%m-%d %H:%M:%S.%f")
            trade_timestamp = int(trade_datetime.timestamp())

            year = trade_datetime.year
            if self.args.only_last_year:
                year_condition = (year == self.args.max_year)
            else:
                year_condition = True

            if year > self.args.max_year:
                print("\nReached end of year {}. Desired timespan processed."
                      .format(self.args.max_year))
                break

            if year not in self.events:
                conprint(year_condition, "\nProfit Report {}".format(year))
                conexport(self.args, year_condition, "\n## Profit Report ``{}``".format(year))

                self.events[year] = {
                    'types': [],
                    'pairs': [],
                    'costs_dfc': [],
                    'gains_dfc': [],
                    'taxes': [],
                    'profits_dfc': [],
                    'profit_year_dfc': 0.0,
                    'taxes_year_dfc': 0.0
                }

            trade_type = trade.type
            sell_trade_base_currency = trade.pair[1:4]
            sell_trade_quote_currency = trade.pair[-3:]

            # Check if the trade has to be handled as a sell
            # Buy of cc_1 with cc_2 is sell of cc_2 for cc_1 (cc2cc_buy)
            sell_condition_cc2cc_buy = (trade_type == "buy" and sell_trade_quote_currency not in FIAT_CURRENCIES)
            sell_condition_cc2cc_sell = (trade_type == "sell" and sell_trade_quote_currency not in FIAT_CURRENCIES)
            sell_condition_cc2fiat_sell = (trade_type == "sell" and sell_trade_quote_currency in FIAT_CURRENCIES)
            if (sell_condition_cc2cc_buy or sell_condition_cc2cc_sell or sell_condition_cc2fiat_sell):
                sell_datetime = trade_datetime
                sell_timestamp = trade_timestamp

                if sell_condition_cc2cc_buy:
                    sell_type = "cc2cc_buy"
                    sell_base_currency = sell_trade_quote_currency
                    sell_quote_currency = sell_trade_base_currency
                    sell_cost = trade.vol
                    sell_volume = trade.cost
                elif sell_condition_cc2cc_sell:
                    sell_type = "cc2cc_sell"
                    sell_base_currency = sell_trade_base_currency
                    sell_quote_currency = sell_trade_quote_currency
                    sell_cost = trade.cost
                    sell_volume = trade.vol
                elif sell_condition_cc2fiat_sell:
                    sell_type = "cc2fiat_sell"
                    sell_base_currency = sell_trade_base_currency
                    sell_quote_currency = sell_trade_quote_currency
                    sell_cost = trade.cost
                    sell_volume = trade.vol

                sell_pair = sell_base_currency + sell_quote_currency

                self.events[year]['types'].append(sell_type)
                self.events[year]['pairs'].append(sell_pair)

                conprint(year_condition, "\n\tSell of {} {} for {} {} on {}"
                         .format(sell_base_currency, sell_volume, sell_quote_currency, sell_cost, sell_datetime))
                conexport(self.args, year_condition, "\n### Sell of ``{} {}`` for ``{} {}`` on ``{}``"
                          .format(sell_base_currency, sell_volume, sell_quote_currency, sell_cost, sell_datetime))

                for key, val_dict in self.ledger[sell_base_currency].items():
                    if val_dict['change'] <= 0:
                        continue

                    buy_timestamp = val_dict['timestamp']
                    buy_type = val_dict['type']
                    buy_pair = val_dict['pair']
                    buy_volume = val_dict['change']

                    buy_datetime = datetime.fromtimestamp(buy_timestamp)
                    buy_trade_base_currency = buy_pair[1:4]
                    buy_trade_quote_currency = buy_pair[-3:]

                    buy_sell_condition_cc2cc_buy = (buy_type == "buy" and buy_trade_quote_currency
                                                    not in FIAT_CURRENCIES)
                    buy_sell_condition_cc2cc_sell = (buy_type == "sell" and buy_trade_quote_currency
                                                     not in FIAT_CURRENCIES)
                    buy_condition_fiat2crypto_buy = (buy_type == "buy" and buy_trade_quote_currency in FIAT_CURRENCIES)
                    if buy_sell_condition_cc2cc_buy:
                        buy_base_currency = buy_trade_base_currency
                    elif buy_sell_condition_cc2cc_sell:
                        buy_base_currency = buy_trade_quote_currency
                    elif buy_condition_fiat2crypto_buy:
                        buy_base_currency = buy_trade_base_currency
                    else:
                        raise Exception("Unknown buy trade type: ", buy_type, buy_pair)

                    new_buy_volume = buy_volume - sell_volume

                    if new_buy_volume > 0.0:
                        sold_buy_volume = sell_volume

                        conprint(year_condition, "\n\t\tSelling {} {} of buy pool of {}"
                                 .format(sell_base_currency, sold_buy_volume, buy_datetime))
                        conexport(self.args, year_condition, "\n#### Selling ``{} {}`` of buy pool of ``{}``"
                                  .format(sell_base_currency, sold_buy_volume, buy_datetime))

                        self.ledger[sell_base_currency][key]['change'] = new_buy_volume
                        new_buy_volume = self.ledger[sell_base_currency][key]['change']
                        sell_volume = 0.0
                    else:
                        sold_buy_volume = buy_volume

                        conprint(year_condition, "\n\t\tSelling {} {} of buy pool of {}"
                                 .format(sell_base_currency, sold_buy_volume, buy_datetime))
                        conexport(self.args, year_condition, "\n#### Selling ``{} {}`` of buy pool of ``{}``"
                                  .format(sell_base_currency, sold_buy_volume, buy_datetime))

                        self.ledger[sell_base_currency][key]['change'] = 0.0
                        new_buy_volume = self.ledger[sell_base_currency][key]['change']
                        sell_volume -= sold_buy_volume

                    buy_pool_status_message = "BUY POOL STATUS"
                    if self.ledger[sell_base_currency][key]['change'] > 0.0:
                        buy_pool_status_message = "Buy pool not yet empty."
                    elif self.ledger[sell_base_currency][key]['change'] == 0.0:
                        buy_pool_status_message = "Buy pool empty, continue with next buy pool."
                    else:
                        raise Exception("Miscalculation - Negative buy pool after sell")
                        break

                    conprint(year_condition, "\n\t\t\tBuy pool before sell: {} {}"
                             .format(sell_base_currency, buy_volume))
                    conexport(self.args, year_condition, "\n* Buy pool before sell: ``{} {}``  "
                              .format(sell_base_currency, buy_volume))

                    conprint(year_condition, "\t\t\tBuy pool after sell: {} {} ({})"
                             .format(sell_base_currency, new_buy_volume, buy_pool_status_message))
                    conexport(self.args, year_condition, "\n* Buy pool after sell: ``{} {}`` ({})  "
                              .format(sell_base_currency, new_buy_volume, buy_pool_status_message))

                    # Buy pool has been fully sold.
                    if new_buy_volume == 0.0:
                        conprint(year_condition,
                                 "\n\t\t\t{} {} have been sold with this sell from buy pool of {}"
                                 .format(buy_base_currency, sold_buy_volume, buy_datetime))
                        conexport(self.args, year_condition,
                                  "\n* ``{} {}`` have been sold with this sell from buy pool of ``{}``  "
                                  .format(buy_base_currency, sold_buy_volume, buy_datetime))

                        conprint(year_condition,
                                 ("\t\t\tThe remaining sell volume of {} {} remains open "
                                  "and will be sold with the next buy pool.")
                                 .format(buy_base_currency, sell_volume))
                        conexport(self.args, year_condition,
                                  ("\n* The remaining sell volume of ``{} {}`` remains open "
                                   "and will be sold with the next buy pool.  ")
                                  .format(buy_base_currency, sell_volume))

                    sold_sell_volume = sold_buy_volume
                    if sell_condition_cc2cc_buy:
                        sell_price = 1/trade.price
                        sell_currency_price_dfc = get_price(sell_base_currency, "EUR", sell_timestamp)
                        sell_cost_dfc = sold_sell_volume * sell_currency_price_dfc
                    elif sell_condition_cc2cc_sell:
                        sell_price = trade.price
                        sell_currency_price_dfc = get_price(sell_base_currency, "EUR", sell_timestamp)

                        sell_cost_dfc = sold_sell_volume * sell_currency_price_dfc
                    elif sell_condition_cc2fiat_sell:
                        sell_price = trade.price
                        sell_currency_price_dfc = sell_price
                        sell_cost_dfc = sold_sell_volume * sell_price

                    buy_currency_price_dfc = get_price(buy_base_currency, "EUR", buy_timestamp)
                    buy_cost_dfc = sold_buy_volume * buy_currency_price_dfc

                    cost_dfc = buy_cost_dfc
                    gain_dfc = sell_cost_dfc
                    profit_dfc = gain_dfc - cost_dfc
                    self.total_profit_dfc += profit_dfc

                    self.events[year]['costs_dfc'].append(cost_dfc)
                    self.events[year]['gains_dfc'].append(gain_dfc)
                    self.events[year]['profits_dfc'].append(profit_dfc)
                    self.events[year]['profit_year_dfc'] += profit_dfc

                    conprint(year_condition, "\n\t\t\tCost: {:.2f} EUR (@ {} EUR / {})"
                             .format(buy_cost_dfc, buy_currency_price_dfc, buy_base_currency))
                    conexport(self.args, year_condition, "\n* Cost: ``{:.2f} EUR`` (@ ``{} EUR / {}``)  "
                              .format(buy_cost_dfc, buy_currency_price_dfc, buy_base_currency))

                    conprint(year_condition, "\t\t\tGain: {:.2f} EUR (@ {} EUR / {})"
                             .format(gain_dfc, sell_currency_price_dfc, sell_base_currency))
                    conexport(self.args, year_condition, "\n* Gain: ``{:.2f} EUR`` (@ ``{} EUR / {}``)  "
                              .format(gain_dfc, sell_currency_price_dfc, sell_base_currency))

                    conprint(year_condition,
                             "\t\t\tProfit: {:.2f} EUR\n".format(profit_dfc))
                    conexport(self.args, year_condition,
                              "\n#### Profit: ``{:.2f} EUR``  ".format(profit_dfc))

                    tax = (profit_dfc * self.args.tax_rate
                           if Taxy.is_taxable_event(buy_timestamp, sell_timestamp)
                           else 0)
                    self.total_taxes_dfc += tax

                    self.events[year]['taxes'].append(tax)
                    self.events[year]['taxes_year_dfc'] += tax

                    if sell_volume == 0.0:
                        break

        for year in self.events:
            conprint(True, "Profit in {}: {:.2f} EUR"
                     .format(year, self.events[year]['profit_year_dfc']))
            conexport(self.args, True, "\n### Profit in {}: ``{:.2f} EUR``"
                      .format(year, self.events[year]['profit_year_dfc']))

            conprint(True, "Taxes in {}: {:.2f} EUR\n"
                     .format(year, self.events[year]['taxes_year_dfc']))
            conexport(self.args, True, "\n### Taxes in {}: ``{:.2f} EUR``"
                      .format(year, self.events[year]['taxes_year_dfc']))

        conprint(True, "\nTotal profit: {:.2f} EUR"
                 .format(self.total_profit_dfc))
        conexport(self.args, True, "\n## Total profit: ``{:.2f} EUR``"
                  .format(self.total_profit_dfc))

        conprint(True, "Total taxes: {:.2f} EUR"
                 .format(self.total_taxes_dfc))
        conexport(self.args, True, "\n## Total taxes: ``{:.2f} EUR``"
                  .format(self.total_taxes_dfc))

    @staticmethod
    def is_taxable_event(buy_timestamp, sell_timestamp):
        taxable = False
        if sell_timestamp <= buy_timestamp + 31536000:
            taxable = True

        return taxable
