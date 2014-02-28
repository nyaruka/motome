from django.db import models
from smartmin.models import SmartModel
from products.models import Product, ProductAddon
from django.contrib.auth.models import User
from django.conf import settings
import datetime
from decimal import Decimal
from customers.models import Location

class Order(SmartModel):
    ORDER_STAGES = (('S', "Started"),    # started placing items in this order
                    ('L', "Located"),    # the user has finalized their order and located themselves
                    ('P', "Paid"),       # order is placed and paid for
                    ('C', "Confirmed"),  # order is confirmed by restaurant
                    ('R', "Recruited"),  # a moto has been recruited to deliver this order
                    ('E', "En Route"),   # the order is on its way to the customer
                    ('D', "Delivered"),  # the order has been delivered
                    ('X', "Cancelled"))  # the order was cancelled

    user = models.ForeignKey(User, null=True,
                             help_text="The user that owns this order, can be null")
    location = models.ForeignKey(Location, null=True,
                                 help_text="Where this order is being delivered to")
    stage = models.CharField(max_length=1, default='S',
                             help_text="The state of this order")

    started_at = models.DateTimeField(null=True,
                                      help_text="When the order was first started")
    paid_at = models.DateTimeField(null=True,
                                   help_text="When the order was paid for")
    confirmed_at = models.DateTimeField(null=True,
                                       help_text="When the order was confirmed by the restaurant")
    recruited_at = models.DateTimeField(null=True,
                                        help_text="When a moto was recruited to deliver this order")
    enroute_at = models.DateTimeField(null=True,
                                      help_text="When the moto picked up the order at the restaurant")
    delivered_at = models.DateTimeField(null=True,
                                        help_text="When the order was delivered")
    cancelled_at = models.DateTimeField(null=True,
                                        help_text="When the order was cancelled")


    @property
    def items(self):
        return self.order_items.filter(is_active=True)

    @property
    def total_value(self):
        total_value = Decimal(0)
        for item in self.items:
            total_value += item.total_value

        # add the delivery fee to the total value
        return total_value

    @property
    def delivery_fee(self):
        return 2000

    @property
    def total_with_delivery(self):
        return self.total_value + self.delivery_fee

    @classmethod
    def from_request(cls, request):
        if 'order_id' in request.session and Order.objects.filter(pk=request.session['order_id']):
            return Order.objects.get(pk=request.session['order_id'])
        else:
            anon_user = User.objects.get(pk=settings.ANONYMOUS_USER_ID)
            order = Order.objects.create(stage='S', started_at=datetime.datetime.now(),
                                         created_by=anon_user,
                                         modified_by=anon_user)
            request.session['order_id'] = order.id
            return order

    def add_single(self, product):
        anon_user = User.objects.get(pk=settings.ANONYMOUS_USER_ID)
        self.order_items.create(product=product, price=product.price, 
                          created_by=anon_user, modified_by=anon_user)

    def __unicode__(self):
        return "%s_%s" % (self.user, self.stage)

class OrderItem(SmartModel):
    order = models.ForeignKey(Order, related_name='order_items',
                              help_text="When this order was placed")
    product = models.ForeignKey(Product,
                                help_text="The product being ordered")
    price = models.DecimalField(max_digits=12, decimal_places=2,
                                help_text="The price of this product, per")

    @property
    def addons(self):
        return self.item_addons.filter(is_active=True)

    def add_on(self, addon):
        anon_user = User.objects.get(pk=settings.ANONYMOUS_USER_ID)
        self.item_addons.create(addon=addon, price=addon.price,
                                created_by=anon_user, modified_by=anon_user)

    def addon_ids(self):
        return [item_addon.addon.id for item_addon in self.addons]

    @property
    def total_value(self):
        return self.price + sum([item_addon.price for item_addon in self.addons.filter(is_active=True)])

    def __unicode__(self):
        return self.product.name


class ItemAddon(SmartModel):
    item = models.ForeignKey(OrderItem, related_name='item_addons',
                             help_text="The item which has an addon")
    addon = models.ForeignKey(ProductAddon, 
                              help_text="The addon itself")
    price = models.DecimalField(max_digits=12, decimal_places=2,
                                help_text="The price of this addon on this order item")

    def __unicode__(self):
        return self.addon.name

