from .models import *
from smartmin.views import *

class ProductCRUDL(SmartCRUDL):
    model = Product
    actions = ('create', 'update', 'list')

    class List(SmartListView):
        fields = ('name', 'store', 'price')

class ProductAddonCRUDL(SmartCRUDL):
    model = ProductAddon
    actions = ('create', 'update', 'list')
    
    class List(SmartListView):
        fields = ('name', 'products', 'price')

        def get_products(self, obj):
            return ", ".join(product.name for product in obj.products.all())
