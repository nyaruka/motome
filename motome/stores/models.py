from django.db import models
from smartmin.models import SmartModel
from django.contrib.auth.models import User
from locales.models import Country

class Store(SmartModel):
    name = models.CharField(max_length=128,
                            help_text="The name of this store")

    description = models.TextField(help_text="A description of this store")

    logo = models.ImageField(upload_to='logos', null=True, blank=True,
                             help_text="The logo for this store")

    splash = models.ImageField(upload_to='splashs', null=True, blank=True,
                             help_text="The splash image for this store")

    country = models.ForeignKey(Country,
                                help_text="The country this store resides in")

    lat = models.DecimalField(max_digits=8, decimal_places=5, null=True, blank=True,
                              help_text="The latitude of this store")
    lng = models.DecimalField(max_digits=8, decimal_places=5, null=True, blank=True,
                              help_text="The longitude of this store")

    managers = models.ManyToManyField(User,
                                      help_text="The users who can manage this store")

    def __unicode__(self):
        return self.name

