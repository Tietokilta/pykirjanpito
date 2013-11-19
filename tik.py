# -*- coding: utf-8 -*-

import requests
import dateutil.parser
from decimal import Decimal
from pyquery import PyQuery as pq

def read_decimal(string):
    string = string.split(' ')[0]
    string = string.replace('.', '')
    string = string.replace(',', '.')
    return Decimal(string)

class TIK:
    def __init__(self, username, password):
        self.session = requests.Session()
        self.session.verify = False # This is bad! :-(
        self.session.post('https://kirjanpito.tietokilta.fi/sessions', data={
            'login': username,
            'password': password,
            'commit': 'Kirjaudu sisään'
        })

    def get_max_id(self):
        rows = self.search('')
        max_id = 0
        for row in rows:
            max_id = max(max_id, int(row['id']))
        return max_id

    def add_entry(
        self,
        description,
        price,
        date,
        credit,
        debit,
        year=2013
    ):
        response = self.session.post('https://kirjanpito.tietokilta.fi/entries/add_to_entries', data={
            'entry[receipt_number]': self.get_max_id()+1,
            'entry[description]': description,
            'entry[sum]': price,
            'entry[date(3i)]': date.split('.')[0],
            'entry[date(2i)]': date.split('.')[1],
            'entry[date(1i)]': date.split('.')[2],
            'entry[fiscal_period_id]': year,
            'debet_account': debit,
            'entry[debet_account_id]': "%s%s" % (year, debit.split(' ')[0]),
            'credit_account': credit,
            'entry[credit_account_id]': "%s%s" % (year, credit.split(' ')[0]),
            '_': ''
        })
        return response

    def search(self, q):
        response = self.session.post('https://kirjanpito.tietokilta.fi/entries/list', data={
            'search': q,
            '_': ''
        })

        #import pudb; pu.db;
        rows = []
        for row in pq(response.text)('.odd_row, .even_row').items():
            tds = []
            for td in pq(row.html()).find('td').items():
                tds.append(td.text())
                #print "Td: %r" % td.text()
            if len(tds) == 7:
                rows.append({
                    'id': tds[0],
                    'message': tds[1],
                    'price': read_decimal(tds[2]),
                    'date': dateutil.parser.parse(tds[3], dayfirst=True),
                    'debit': tds[4],
                    'credit': tds[5]
                })

        return rows

