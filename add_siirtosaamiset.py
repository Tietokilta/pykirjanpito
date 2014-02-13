# -§*- coding: utf-8 -*-
import operator
import argparse
import json
import re
import sys
import tik
from configuration import configuration

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

add_events = []
with open('siirtosaamiset.txt') as saamiset:
    for saaminen in saamiset:
        event_name, name, email, amount, _ = saaminen.split("\t", 4)
        pair = analyze_transaction({
            u'message': '%s' % (event_name),
            u'sign': '+'
        })
        event_name = event_name.replace('\xe4', 'ä')
        event_name = event_name.replace('\xf6', 'ö')
        name = name.replace('\xe4', 'ä')
        name = name.replace('\xf6', 'ö')
        add_events.append({
            'description': 'Siirtosaaminen, %s, %s' % (event_name, name),
            'price': amount.replace(',', '.'),
            'debit': '2100 Siirtosaamiset',
            'credit': pair[1],
            'date': '31.12.2013'
        })

print add_events
print "Connecting..."
tikapi = tik.TIK(configuration['username'], configuration['password'])


for event in add_events:
    print "Adding transaction %r" % event
    #print repr(event['description'])
    #break
    tikapi.add_entry(
        description=event['description'],
        price=event['price'],
        date=event['date'],
        debit=event['debit'],
        credit=event['credit'],
        year=2013
    )