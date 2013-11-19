# -*- coding: utf-8 -*-

import argparse
import datetime
import tik
import re
import sys
import database
from decimal import Decimal
from validate_email import validate_email
from database import db
from models import Event, Order

event_name = raw_input("Tapahtuman nimi: ")
keyword = raw_input("Keyword: ")
regular_expression = raw_input("Regular Expression: ")
price = raw_input("Price: ")
lines = ""
empty = 0
while True:
    line = raw_input("Data: ")
    lines += "\n"+line
    if empty >= 2:
        break
    if line == "":
        empty += 1
    else:
        empty = 0

users = []

for row in lines.split("\n"):
    columns = row.split("\t")
    name = columns[0]
    email = None
    for column in columns:
        if validate_email(column):
            email = column

    if name and email:
        users.append((
            name,
            email
        ))


lines = ""
empty = 0
while True:
    line = raw_input("Email filter: ")
    lines += "\n"+line
    if empty >= 2:
        break
    if line == "":
        empty += 1
    else:
        empty = 0

if lines.replace("\r","").replace("\n","").replace("\t","").replace(" ","") == "":
    email_filter = None
else:
    email_filter = []
    for row in lines.split("\n"):
        row = row.strip().replace(",","")
        if '<' in row:
            email = row.split('<')[1].split('>')[0]
        else:
            email = row
        email_filter.append(email)

    print "At first, users: %s" % len(users)
    users = filter(
        lambda x: x[1] in email_filter,
        users
    )
    print "===> %s" % len(users)


print "-----------------"
print """
Name: %s
Keyword: %s
RegExp: %s
Users Total: %s
Price: %s

""" % (
    event_name,
    keyword,
    regular_expression,
    len(users),
    price,
)

do_you = raw_input("Continue y/n?")
if do_you == "y":
    event = Event(
        name=event_name,
        keyword=keyword,
        regular_expression=regular_expression,
        price=Decimal(price)
    )
    db.session.add(event)
    db.session.flush()

    for user in users:
        order = Order(
            event=event,
            name=user[0],
            email=user[1],
            is_paid=False
        )
        db.session.add(order)
        db.session.flush()

    db.session.commit()
    print "Added!"