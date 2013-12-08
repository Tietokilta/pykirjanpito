# -*- coding: utf-8 -*-
import operator
import argparse
import json
import re
import sys
import tik
from configuration import configuration

parser = argparse.ArgumentParser()
parser.add_argument("filename")
args = parser.parse_args()

with open(args.filename) as fp:
    transactions = json.loads(fp.read())

def analyze_transaction(tr, replace_invalid=False):
    DUMP_NONE = u'1030 - Virheelliset tilitapahtumat'
    
    debit = credit = None
    if tr[u'sign'] == '+':
        debit = u'2050 Handelsbanken'
        if re.search(u'Jäsenmaksu|registration fee', tr[u'message'], re.IGNORECASE):
            credit = u'1110 Jäsenmaksut'
        elif re.search(u'PowerBussi', tr[u'message'], re.IGNORECASE):
            credit = u'0171 - Powerkähmyt'
        elif re.search(u'Juusto', tr[u'message'], re.IGNORECASE):
            credit = u'0350 Maisteluillat'
        elif re.search(u'Opera|Ooppera|figaro', tr[u'message'], re.IGNORECASE):
            credit = u'0300 Teatteri, ooppera jne.'
        elif re.search(u'miekkailu', tr[u'message'], re.IGNORECASE):
            credit = u'0360 Liikuntatoiminta'
        elif re.search(u'bp|lenski', tr[u'message'], re.IGNORECASE):
            credit = u'0670 Baltian Pitkä ja Lenski'
        elif re.search(u'Muisti|Välimuistinnollaus|M0', tr[u'message'], re.IGNORECASE):
            credit = u'0200 Muistinnollaus ja välimuistinnollaus'
        elif re.search(u'cruise|kruise', tr[u'message'], re.IGNORECASE):
            credit = u'0230 Kiltaristeilyt'
        elif re.search(u'kyykkä|titeeni|hesari|aatu|appro', tr[u'message'], re.IGNORECASE):
            credit = u'0660 Excursiot, ATK-YTP ja NUCC'
        elif re.search(u'megazone', tr[u'message'], re.IGNORECASE):
            credit = u'0360 Liikuntatoiminta'
        elif re.search(u'speksi', tr[u'message'], re.IGNORECASE):
            credit = u'0315 Speksit'
    elif tr[u'sign'] == '-':
        credit = u'2050 Handelsbanken'
        if re.search(u'Muisti|Välimuistinnollaus|M0', tr[u'message'], re.IGNORECASE):
            debit = u'0200 Muistinnollaus ja välimuistinnollaus'
        elif re.search(u'OK20|Gorsu|sauna', tr[u'message'], re.IGNORECASE):
            debit = u'0260 AYY-tilavuokrat'
        elif re.search(u'palvelumaksut', tr[u'message'], re.IGNORECASE):
            debit = u'1040 Pankkipalvelumaksut'
        elif re.search(u'Vuju|vuosijuhla', tr[u'message'], re.IGNORECASE):
            debit = u'0600 - Vuosijuhlaedustus'

    if replace_invalid:
        if debit is None:
            debit = DUMP_NONE
        if credit is None:
            credit = DUMP_NONE

    return (debit, credit)

# Fix "OTOT"
date = None
for transaction in transactions:
    if u'sign' in transaction and transaction['message']:
        if transaction['date'] == "OTOT":
            if not date:
                raise Exception("Could not figure out DATE")
            transaction['date'] = date
            print "Fixed transaction #%s %s" % (
                transaction['id'],
                transaction['message']
            )
        else:
            date = transaction['date']

# First we run check where everything is placed
stats = {}
example = {}
total = 0
for transaction in transactions:
    if u'sign' in transaction and transaction['message']:
        pair = analyze_transaction(transaction)
        if not pair in stats:
            stats[pair] = 0
        stats[pair] += 1
        example[pair] = transaction
        total += 1

print "~~~ Parsed %s transactions. ~~~" % total
for k, v in reversed(sorted(stats.iteritems(), key=operator.itemgetter(1))):
    print u"%s <= %s (%s) (%s)" % (k[0], k[1], v, example[k]['message'])

r = raw_input("Do you wish to continue? y/n\n> ")
if r != 'y':
    print "Aborting!"
    sys.quit()

print "Connecting..."
tikapi = tik.TIK(configuration['username'], configuration['password'])

print tikapi.get_max_id()

for transaction in transactions:
    if u'sign' in transaction and transaction['message']:
        print "Adding transaction %r" % transaction
        pair = analyze_transaction(transaction, replace_invalid=True)
        tikapi.add_entry(
            description=transaction['message'].lower().title(),
            price=transaction['amount'],
            date=transaction['date'],
            debit=pair[0],
            credit=pair[1],
            year=2013
        )

