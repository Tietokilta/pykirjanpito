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

class InvalidLoginError(Exception): pass
class ServerError(Exception): pass

class TIK:
    def __init__(self, username, password):
        self.session = requests.Session()
        self.session.verify = False # This is bad! :-(
        self.session.headers.update({'User-Agent': 'pykirjanpito'})
        self.session.get('https://kirjanpito.tietokilta.fi/')

        response = self.session.post('https://kirjanpito.tietokilta.fi/sessions', data={
            'login': username,
            'password': password,
            'commit': 'Kirjaudu sisään'
        })
        self.session.get('https://kirjanpito.tietokilta.fi/accounts/list?new_fiscal_period=2013')
        #if response.status_code != 302:
        #    raise InvalidLoginError(response)

    def _check_response(self, response):
        if (
            response.status_code != 200 or
            'You are not logged in' in response.text
        ):
            raise ServerError(response)

    def get_max_id(self):
        rows = self.search('')
        max_id = 0
        for row in rows:
            max_id = max(max_id, int(row['id']))
        return max_id

    def get_form_values(self, raw_id):
        response = self.session.get('https://kirjanpito.tietokilta.fi/entries/edit/%s' % raw_id)
        if response.status_code != 200:
            raise ServerError(response)
        form_data = {}
        for input_ in pq(response.text)('#content form input, #content form select, #content form textarea').items():
            name = input_.attr('name')
            value = input_.val()
            if value is None:
                value = pq(input_.html()).find('option:selected').val()
            if name:
                form_data[name] = value
        return form_data

    def set_form_values(self, raw_id, form_data):
        response = self.session.post('https://kirjanpito.tietokilta.fi/entries/update/%s' % raw_id, data=form_data)
        self._check_response(response)
        return response
        #print response.text

    def add_entry(
        self,
        description,
        price,
        date,
        credit,
        debit,
        year=2013
    ):
        dateyear = date.split('.')[2]
        if len(dateyear) == 2:
            dateyear = '20' + dateyear
        response = self.session.post('https://kirjanpito.tietokilta.fi/entries/add_to_entries', data={
            'entry[receipt_number]': self.get_max_id()+1,
            'entry[description]': description,
            'entry[sum]': price,
            'entry[date(3i)]': date.split('.')[0],
            'entry[date(2i)]': date.split('.')[1],
            'entry[date(1i)]': year,
            'entry[fiscal_period_id]': dateyear,
            'debet_account': debit,
            'entry[debet_account_id]': "%s%s" % (year, debit.split(' ')[0]),
            'credit_account': credit,
            'entry[credit_account_id]': "%s%s" % (year, credit.split(' ')[0]),
            '_': ''
        })
        self._check_response(response)
        return response

    def search(self, q):
        response = self.session.post('https://kirjanpito.tietokilta.fi/entries/list', data={
            'search': q,
            '_': ''
        })
        self._check_response(response)
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

