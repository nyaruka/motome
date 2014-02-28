from decimal import *

from rapidsms.apps.base import AppBase
from .models import *
from nsms.text import gettext as _
from nsms.parser import Parser, ParseException
from nsms.utils import get_connection_user
from rapidsms.models import Backend, Connection
from django.utils import translation
from rapidsms_httprouter.router import get_router
from django.template import Template, Context
from django.conf import settings
from django.contrib.auth.models import User
from customers.models import Customer
from orders.models import Order
from transactions.models import Credit, Debit

from django.core.exceptions import ObjectDoesNotExist

class App(AppBase):
    def handle (self, message):
        connection = message.connection

        # check if message is from mobile money
        if connection.identity != 'mobilemoney':
            message.respond("You are not a motome user, this message is not supposed to be proccessed. You can use your credit by visiting 'motome.nyaruka.com'")
            return False

        # make a message parsable easily
        # replace newline characters within the message text
        message_line= message.text.replace('\n', ' ').replace('.', '').replace(',', '').split(' ')

        if len(message_line) != 14:
            message.respond("This message doesn't contain a valid transaction.")
            return False            

        # extract and format deterministic parts amount sent, phone used to send amount
        if not message_line[4].isdigit() and not message_line[6].isdigit() and len(message_line[6]) != 10:
            message.respond("This message doesn't contain a valid transaction.")
            return False

        # it is concluded that the message is from mobile money
        credit_amount = Decimal(message_line[4])
        username = '25%s' % message_line[6]

        creditor, status = User.objects.get_or_create(username=username)
        credit = Credit.objects.create(phone=username ,amount=credit_amount, creditor=creditor, created_by=creditor, modified_by=creditor)

        message.respond("Thank you. Your motome account has been credited, you can use this credit to order on motome.")
        return True
