from django.conf.urls.defaults import *

from .views import *

# set up our url patterns
urlpatterns = CountryCRUDL().as_urlpatterns()
urlpatterns += CurrencyCRUDL().as_urlpatterns()
