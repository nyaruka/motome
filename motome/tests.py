from django.test import TestCase
from decimal import Decimal
from locales.models import *
from stores.models import *
from products.models import *
from django.core.urlresolvers import reverse
from nsms.tests import NSMSTest
import datetime

class MotomeTestCase(NSMSTest):
    
    def setUp(self):
        super(MotomeTestCase, self).setUp()

        self.rwf = Currency.objects.create(name="Rwandan Francs",
                                           currency_code='RWF',
                                           abbreviation='RWF',
                                           has_decimals=False,
                                           prefix="",
                                           suffix=" RWF",
                                           created_by=self.admin,
                                           modified_by=self.admin)

        self.usd = Currency.objects.create(name="US Dollars",
                                           currency_code='USD',
                                           abbreviation='US$',
                                           has_decimals=True,
                                           prefix="$",
                                           suffix="",
                                           created_by=self.admin,
                                           modified_by=self.admin)

        self.rwanda = Country.objects.create(name="Rwanda",
                                             country_code='RW',
                                             currency=self.rwf,
                                             calling_code='250',
                                             phone_format='#### ## ## ##',
                                             national_id_format='# #### # ####### # ##',
                                             bounds_zoom='6',
                                             bounds_lat='-1.333',
                                             bounds_lng='29.232',
                                             created_by=self.admin,
                                             modified_by=self.admin)

        self.ksh = Currency.objects.create(name="Kenyan Shillings",
                                           currency_code='KSH',
                                           has_decimals=False,
                                           prefix="",
                                           suffix=" KSH",
                                           created_by=self.admin,
                                           modified_by=self.admin)

        self.kenya = Country.objects.create(name="Kenya",
                                             country_code='KE',
                                             currency=self.ksh,
                                             calling_code='254',
                                             phone_format='#### ## ## ##',
                                             national_id_format='# #### # ####### # ##',
                                             bounds_zoom='6',
                                             bounds_lat='-1.333',
                                             bounds_lng='29.232',
                                             created_by=self.admin,
                                             modified_by=self.admin)

        self.meze_fresh = Store.objects.create(name="Meze Fresh",
                                               country=self.rwanda,
                                               description="Meze Fresh, we make delicious burritos!",
                                               created_by=self.admin,
                                               modified_by=self.admin)


        self.c_burrito = Product.objects.create(name="Chicken Burrito",
                                                store=self.meze_fresh,
                                                description="Burrito full of chicken meats",
                                                price=4200,
                                                created_by=self.admin,
                                                modified_by=self.admin)
        

        self.s_burrito = Product.objects.create(name="Steak Burrito",
                                                store=self.meze_fresh,
                                                description="Burrito full of beef meats",
                                                price=4200,
                                             created_by=self.admin,
                                             modified_by=self.admin)

        self.addon_one = ProductAddon.objects.create(name="Sour Cream", price=500, created_by=self.admin, modified_by=self.admin)
        self.addon_one.products.add(self.c_burrito)
        self.addon_one.products.add(self.s_burrito)
        self.addon_one.save()

        self.addon_two = ProductAddon.objects.create(name="Onion + Green paper", price=0, created_by=self.admin, modified_by=self.admin)
        self.addon_two.products.add(self.c_burrito)
        self.addon_two.products.add(self.s_burrito)
        self.addon_two.save()

        self.addon_tree = ProductAddon.objects.create(name="Guacamole", price=500,  created_by=self.admin, modified_by=self.admin)
        self.addon_tree.products.add(self.c_burrito)
        self.addon_tree.products.add(self.s_burrito)
        self.addon_tree.save()

