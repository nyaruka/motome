from smartmin.views import *
from .models import *

class CreditCRUDL(SmartCRUDL):
    model = Credit
    actions = ('create', 'list', 'update')
    permissions = True

class DebitCRUDL(SmartCRUDL):
    model = Debit
    actions = ('create', 'list', 'update')
    permissions = True
