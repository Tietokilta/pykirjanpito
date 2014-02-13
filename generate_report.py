# -*- coding: utf-8 -*-

import argparse
import datetime
import glob
import tik
import re
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from jinja2 import Template
import database
from configuration import configuration
from database import db
from models import Event, Order

print "Connecting ..."
#tikapi = tik.TIK(configuration['username'], configuration['password'])

events = db.session.query(Event).all()
def render(from_file, to_file):
    with file(from_file) as tmp:
        data = tmp.read().decode('utf-8')
        template = Template(data)
    with file(to_file, 'w') as newfp:
        newfp.write(template.render(events=events))

render('guild_support_template.html', 'guild_support.html')
render('missing_payments_template.html', 'missing_payments.html')

print "Done!"