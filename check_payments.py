# -*- coding: utf-8 -*-

import argparse
import datetime
import tik
import re
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
asd = tikapi.search('speksi')

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
print
print "=== SHAME LIST ==="

for order in db.session.query(Order).filter(
    Order.event_id == args.event_id,
    Order.is_paid != True
):
    print order.name

emails = [order.email for order in db.session.query(Order).filter(
    Order.event_id == args.event_id,
    Order.is_paid != True
)]

print "=== EMAIL === "
print ", ".join(emails)
print """Hei!

Kirjanpitomme mukaan ette ole vielä maksaneet tapahtuman %s ilmottautumismaksua. Maksathan allaolevien ohjeiden mukaisesti mahdollisimman pian.

Saaja: Tietokilta ry
IBAN: FI44 3131 3001 5440 71
BIC: HANDFIHH
Summa: %s
Viesti: %s, <nimi>

Ongelmatapauksissa minuun voi olla yhteydessä.""" % (
    event.name,
    event.price,
    event.keyword
)