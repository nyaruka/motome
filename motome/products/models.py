from django.db import models
from smartmin.models import SmartModel
from stores.models import Store

class Product(SmartModel):
    store = models.ForeignKey(Store,
                              help_text="The store that sells this product")
    name = models.CharField(max_length=128,
                            help_text="The name of this product")
    description = models.TextField(help_text="A brief description of this product")

    price = models.DecimalField(max_digits=12,
                                decimal_places=2,
                                help_text="The price of this product")

    image = models.ImageField(upload_to='previews',
                                help_text="An image of this item when delivered")

    def __unicode__(self):
        return self.name

class ProductAddon(SmartModel):
    products = models.ManyToManyField(Product, related_name='addons',
                                      help_text="The product this addon applies to")
    name = models.CharField(max_length=128,
                            help_text="The name of this add on")
    price = models.DecimalField(max_digits=12,
                                decimal_places=2,
                                help_text="The price of this addon")

    def __unicode__(self):
        return self.name


