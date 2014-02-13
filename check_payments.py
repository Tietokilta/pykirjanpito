# -*- coding: utf-8 -*-

import argparse
import datetime
import glob
import tik
import re
import os
import sys
import database
from configuration import configuration
from database import db
from models import Event, Order

parser = argparse.ArgumentParser()
parser.add_argument("event_id", type=int)
args = parser.parse_args()

event = db.session.query(Event).get(args.event_id)

print "Connecting ..."
tikapi = tik.TIK(configuration['username'], configuration['password'])
print "Searching ..."

def find_match(results, match):
    for result in results:
        if re.search(match, result[u'message'], re.IGNORECASE):
            return result
    return None

def swapped(string):
    return " ".join(reversed(string.split(" ")))

paid = 0
warnings = []
for order in db.session.query(Order).filter(
    Order.event_id == args.event_id,
    Order.is_paid != True
):
    order.last_checked = datetime.datetime.now()
    sys.stdout.write('.')
    sys.stdout.flush()
    for search_term in (
        order.name.replace("\xe4",'ä'),
        swapped(order.name.replace("\xe4",'ä'))
    ):
        search_results = tikapi.search(
            search_term
        )
        match = find_match(
            search_results,
            event.regular_expression
        )
        if match:
            if match['price'] >= event.price:
                order.is_paid = True
                order.paid_date = match['date']
                order.payment = match['price']
                if not order.comments:
                    order.comments = "#%s" % match['id']
                else:
                    order.comments += " #%s" % match['id']
            else:
                warnings.append(match)
            break

db.session.commit()

print "\n"
print "=== WARNINGS ==="
for warning in warnings:
    print warning

print "=== STATS ==="
print "%s total" % db.session.query(Order).filter(
    Order.event_id == args.event_id
).count()
print "%s has paid" % db.session.query(Order).filter(
    Order.event_id == args.event_id,
    Order.is_paid == True
).count()
print "%s has NOT paid" % db.session.query(Order).filter(
    Order.event_id == args.event_id,
    Order.is_paid != True
).count()

print "=== UNMATCHED ==="
results = tikapi.search(event.keyword)
for result in results:
    has_match = False
    
    for order in db.session.query(Order).filter(
        Order.event_id == args.event_id
    ):
        if order.name.decode('utf-8').lower() in result['message'].lower():
            if not order.is_paid:
                print "****" * 20
                print order
            has_match = True
            break

    if not has_match:
        print result
if not results:
    print "No results were found for keyword %r" % event.keyword
    print "This could indicate wrong keyword or the server is hanging up. Cancelling..."
    sys.exit()

print
print "=== SHAME LIST ==="

for order in db.session.query(Order).filter(
    Order.event_id == args.event_id,
    Order.is_paid != True
):
    print "%s <%s>" % (order.name, order.email)

emails = [order.email for order in db.session.query(Order).filter(
    Order.event_id == args.event_id,
    Order.is_paid != True
)]


if 'txt_folder' in configuration and configuration['txt_folder']:
    print "=== SEARCHING SHAME LIST IN .TXT ==="
    for order in db.session.query(Order).filter(
        Order.event_id == args.event_id,
        Order.is_paid != True
    ):
        last_name = order.name.split(" ")[-1]
        print "* %s" % order.name
        for file_ in glob.glob(configuration['txt_folder']+'*.txt'):
            with open(file_) as fp:
                lines = fp.readlines()
                for line in lines:
                    if last_name.lower() in line.lower():
                        print "%s%s: %s" % (
                            '*.#'*40 if event.keyword in line or str(event.price) in line else '',
                            os.path.basename(file_),
                            line
                        )


print "=== EMAIL === "
print ", ".join(emails)
print """Hei! / Hey!

Kirjanpitomme mukaan ette ole vielä maksaneet tapahtuman %(name)s maksua. Maksathan allaolevien ohjeiden mukaisesti mahdollisimman pian. / According to our accounting, you haven't paid event %(name)s.

Saaja (recipient): Tietokilta ry
IBAN: FI44 3131 3001 5440 71
BIC: HANDFIHH
Summa (amount): %(amount)s
Viesti (message): %(keyword)s, <name>

Ongelmatapauksissa minuun voi olla yhteydessä. Hyvää joulua!""" % {
    'name': event.name,
    'amount': event.price,
    'keyword': event.keyword
}