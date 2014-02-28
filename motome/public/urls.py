from .views import *

urlpatterns = patterns('', 
    url(r'^$', home, name='public_home'),
    url(r'^checkout', checkout, name='public_checkout'),
    url(r'^login', login, name='public_login'),
    url(r'^cart', cart, name='public_cart'),
    url(r'^pay/(\d+)/', pay, name='public_pay'),
    url(r'^success/', success, name='public_success'),
    url(r'^confirm/(\d+)/', confirm, name='public_confirm'),
)

urlpatterns += LocationCRUDL().as_urlpatterns()
