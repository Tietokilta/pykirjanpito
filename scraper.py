# -*- coding: utf-8 -*-

import argparse
import datetime
import glob
import tik
import re
import os
import sys
import dateutil
import yaml
import database
from pyquery import PyQuery as pq
from configuration import configuration
from database import db
from models import Event, Order


"""
tikapi = tik.TIK(configuration['username'], configuration['password'])

rows = []
for i in range(1, 15):
    url = 'https://kirjanpito.tietokilta.fi/entries/list?page=%s' % i
    response = tikapi.session.get(url)
    tikapi._check_response(response)
    for row in pq(response.text)('.odd_row, .even_row').items():
        tds = []
        for td in pq(row.html()).find('td').items():
            tds.append(td.text())
            #print "Td: %r" % td.text()
        if len(tds) == 7:
            rows.append({
                'id': tds[0],
                'message': tds[1],
                'price': tik.read_decimal(tds[2]),
                'date': dateutil.parser.parse(tds[3], dayfirst=True),
                'debit': tds[4],
                'credit': tds[5]
            })
with open('accountData.yml', 'w') as outfile:
    outfile.write(yaml.dump(rows, default_flow_style=True))
"""

try:
    print "Reading from old data..."
    with open('accountData.yml') as openfile:
        rows = yaml.load(openfile)
except IOError:
    print "Fetching new data"
    tikapi = tik.TIK(configuration['username'], configuration['password'])

    rows = []
    for i in range(1, 16):
        url = 'https://kirjanpito.tietokilta.fi/entries/list?page=%s' % i
        response = tikapi.session.get(url)
        tikapi._check_response(response)
        for row in pq(response.text)('.odd_row, .even_row').items():
            tds = []
            for td in pq(row.html()).find('td').items():
                tds.append(td.text())
                #print "Td: %r" % td.text()
            if len(tds) == 7:
                rows.append({
                    'id': tds[0],
                    'message': tds[1],
                    'price': tik.read_decimal(tds[2]),
                    'date': dateutil.parser.parse(tds[3], dayfirst=True),
                    'debit': tds[4],
                    'credit': tds[5]
                })
    with open('accountData.yml', 'w') as outfile:
        outfile.write(yaml.dump(rows, default_flow_style=True))

def get_unique_accounts(rows):
    accounts = {}
    for row in rows:
        if not row['debit'] in accounts:
            accounts[row['debit']] = True
        if not row['credit'] in accounts:
            accounts[row['credit']] = True
    return accounts.keys()

def get_debit_credit(rows, account):
    debit = credit = 0
    example = None
    for row in rows:
        if row['debit'] == account:
            debit += row['price']
            example = row['message']
        if row['credit'] == account:
            credit += row['price']
            example = row['message']
    return (debit, credit, example)

accounts = get_unique_accounts(rows)
total_debit = 0
total_credit = 0
with open('scraper.txt', 'w') as outfile:
    for account in sorted(accounts):
        debit, credit, example = get_debit_credit(rows, account)
        outfile.write("%s\t%s\t%s\t%s\n" % (
            account.encode('ascii', 'ignore'),
            debit,
            credit,
            example.encode('ascii', 'ignore')
        ))
        total_debit += debit
        total_credit += credit
print "Total\t%s\t%s" % (total_debit, total_credit)