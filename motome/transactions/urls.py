from django.conf.urls.defaults import *

from .views import *

# set up our url patterns
urlpatterns = CreditCRUDL().as_urlpatterns()
urlpatterns += DebitCRUDL().as_urlpatterns()
