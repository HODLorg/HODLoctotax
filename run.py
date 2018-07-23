#!/usr/bin/python3
# -*- coding: utf-8 -*-

from octotax.dataimport import import_kraken_trades
from octotax.profits import Taxy
from octotax.utils import get_args, start_up, export_pdf, clean_up


args = get_args()

start_up()

import_kraken_trades()

tax = Taxy(args)
tax.calculate_profit()
tax.calculate_fees()

if args.export:
    export_pdf()

clean_up()
