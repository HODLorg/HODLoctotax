#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import configargparse
import pdfkit

from markdown import markdown as md


def get_args():
    parser = configargparse.ArgParser()
    parser.add_argument("-it", "--input-type", type=str, default="trades",
                        help="Set input file type (trades or ledger).")
    parser.add_argument("-m", "--method", type=str, default="FIFO",
                        help="Set profit calculation method.")
    parser.add_argument("-tr", "--tax-rate", type=int, default=0.4,
                        help="Set tax rate.")
    parser.add_argument("-dfc", "--default-fiat_currency", type=str, default="EUR",
                        help="Set default fiat currency.")
    parser.add_argument("-my", "--max-year", type=int, default=2018,
                        help="Set year for calculuation.")
    parser.add_argument("-oly", "--only-last-year", action="store_true", default=False,
                        help="Calculates profit only for the last year")
    parser.add_argument("-exp", "--export", action="store_true", default=False,
                        help="Exports the result in markdown format.")
    args = parser.parse_args()

    return args


def conprint(condition, content):
    if condition:
        print(content)


def conexport(args, condition, content):
    if args.export and condition:
        content = content.replace("\t\t\t", "#### ")
        content = content.replace("\t\t", "### ")
        content = content.replace("\t", "## ")
        with open("data/export/report.md", 'a') as f:
            f.write(content)


def export_pdf():
    if os.path.isfile("data/export/report.md"):
        print("Generating PDF report ...")
        with open("data/export/report.md", 'r') as f:
            html_text = md(f.read(), output_format="html4")
            pdfkit.from_string(html_text, "data/export/report.pdf")
    else:
        print("No pdf export possible: markdown report file missing.")


def start_up():
    if os.path.isfile("data/export/report.md"):
        os.remove("data/export/report.md")


def clean_up():
    if os.path.isfile("data/temp/trades.csv"):
        os.remove("data/temp/trades.csv")

    if os.path.isfile("data/temp/ledger.csv"):
        os.remove("data/temp/ledger.csv")
