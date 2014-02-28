from .models import *
from smartmin.views import *
from locales.models import Country

class OrderCRUDL(SmartCRUDL):
    model = Order
    actions = ('read', 'update', 'list', 'print')

    class Print(SmartReadView):
        default_template = 'public/confirm.html'

        def get_context_data(self, *args, **kwargs):
            context = super(OrderCRUDL.Print, self).get_context_data(*args, **kwargs)
            context['user'] = self.object.user
            context['country'] = Country.objects.get(name="Rwanda")
            context['currency'] = context['country'].currency
            return context

    class List(SmartListView):
        fields = ('id', 'status', 'user', 'started_at', 'total_value')
