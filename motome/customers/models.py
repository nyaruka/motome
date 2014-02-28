from django.contrib.auth.models import User
from rapidsms.models import Connection, Backend
from rapidsms_httprouter.router import get_router
from smartmin.models import SmartModel
from django.db import models

class Customer(User):

    def send_password(self):
        # generate a one time use password
        password = User.objects.make_random_password(length=6, allowed_chars='1234567890')
        self.set_password(password)
        self.save()

        # send the SMS out
        (backend, created) = Backend.objects.get_or_create(name='mtn_3071')
        (connection, created) = Connection.objects.get_or_create(backend=backend, identity=self.username)
        get_router().add_outgoing(connection, "Your motome password is: %s %s %s" % (password[:2], password[2:4], password[4:]))

    @classmethod
    def get_or_create_customer(cls, phone_number):
        customers = Customer.objects.filter(username=phone_number)
        if customers:
            customer = customers[0]
            customer.save()
            return customer

        customer = Customer.objects.create_user(phone_number)
        customer.set_unusable_password()
        customer.save()
        return customer

    class Meta:
        proxy = True

class Location(SmartModel):
    user = models.ForeignKey(User, null=True, blank=True,
                             help_text="The customer this location is for")
    nickname = models.CharField(max_length=32,
                                help_text="The nickname for this location")
    building = models.CharField(max_length=32, null=True, blank=True,
                             help_text="The building from which you live or work in. e.g. MTN Center")
    business = models.CharField(max_length=32, null=True, blank=True,
                             help_text="The name of the business or organization inside the building. e.g. Burbon Coffee")
    hints = models.TextField(max_length=1024,
                             help_text="Any tips for the driver, the color of your gate, nearby landmarks")
    lat = models.DecimalField(max_digits=8, decimal_places=5, null=True, blank=True,
                              help_text="The latitude of this store")
    lng = models.DecimalField(max_digits=8, decimal_places=5, null=True, blank=True,
                              help_text="The longitude of this store")    
