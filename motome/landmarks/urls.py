from django.conf.urls.defaults import *

from .views import *

# set up our url patterns
urlpatterns = LandmarkTypeCRUDL().as_urlpatterns()
urlpatterns += LandmarkCRUDL().as_urlpatterns()
