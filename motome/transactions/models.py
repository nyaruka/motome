from django.db import models
from smartmin.models import SmartModel
from django.contrib.auth.models import User
from orders.models import Order

class Credit(SmartModel):
    phone = models.CharField(max_length=12, help_text="The phone number of the creditor")
    amount = models.DecimalField(max_digits=10, decimal_places=0,
                                 help_text="The amount of credit sent within this transaction")
    creditor = models.ForeignKey(User, null=True, blank=True,
                                 help_text="Owner of the amount within this transaction")
    
class Debit(SmartModel):
    credit = models.ForeignKey(Credit, null=True, blank=True, related_name='debits', help_text="Where to debit from")
    amount = models.DecimalField(max_digits=10, decimal_places=0,
                                 help_text="The amount of credit sent within this transaction")
    order = models.ForeignKey(Order, help_text="The order that defines this transaction")
    customer = models.ForeignKey(User, help_text="The customer responsible of this transaction")

