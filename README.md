# Octotax
The tax calculator for inter EURO crypto and cross crypto trades on the *kraken.com* exchange.

## The Project
This project focuses on easy annual tax report generation based on data from cryptocurrency exchanges. It aims to set competition to paid apps. The calculation uses the taxHowever, it will **not** serve as a hand-in report generator for your national tax administration.

## Disclaimer
This project, code, procedures and results are **not** to be regarded as financial, accounting or tax advise for your country!

## Installation
Prerequisites: git and Python 3.

1. Clone the repository
2. Install its dependencies via ``pip install -r requirements.txt``

## Running
 0.  Export your trades from the *kraken.com* exchange inside your account area. Download the trades in the ``.csv`` format, not the ledger. We do promise that the code does **not and never** upload your trading values to any external machine. Note, that price queries of the cryptocurrencies of your trades are made against against *cryptocompare.com*, at least once, to gather the needed data for earnings and profits calculations. Also note that proper tax calculation via the FIFO method does need a full or at least fully independent trading history.
 2.  Place the ``trades.csv`` file into the ``data/raw/`` directory.
 3.  Run the python script via ``python3 run.py``. Note that there are options which you can specify, see below.
 4.  Watch the cli output, look into ``data/export/`` if you exported the data. You can also find the used prices in ``data/history/`` which are used in the calculation as references.

### Options
You can specify options as arguments to your cli call via for example ``--option``, or in short ``-opt``. A detailed list can be found in the file ``octotax/utils.py``.
 * ``--year 1234`` - specifies the year ``1234`` which you want to report alone. By default all years will be reported in the output.
 * ``--export`` - outputs a MarkDown ``report.md`` as well as a PDF ``report.pdf`` into the ``data/export/`` directory.
 * ``--tax-rate 50`` - specifies the tax rate which will be applied to your profits.

### Notes
The directory ``data/temp/`` is for data transfer in between modules for large trading history data files to not abuse RAM of your machine.

## Participate!
This is an open source project and you are invited to participate. If you find a bug do not hesitate to submit and issue or even fix it yourself and make a pull request. If you want to extend the program to another exchange, fiat currency or just have feature requests, please make an issue or pull request if you already have working code.

Best regards,
HODL team

(We are **not** affiliated with the *hodlbot-io* website in any way. Actually we've been around here before their webpage.)
