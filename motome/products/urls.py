from .views import *

urlpatterns = ProductCRUDL().as_urlpatterns()
urlpatterns += ProductAddonCRUDL().as_urlpatterns()
