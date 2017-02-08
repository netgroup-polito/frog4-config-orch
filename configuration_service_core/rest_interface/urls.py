from django.conf.urls import url
from configuration_service_core.rest_interface import views

urlpatterns = [
                   url(r'^vnf/(?P<vnf_id>[^/]+)/(?P<graph_id>[^/]+)/(?P<tenant_id>[^/]+)/$', views.ConfigureVNF.as_view(), name='Configure VNF'),
                   url(r'^status/(?P<vnf_id>[^/]+)/(?P<graph_id>[^/]+)/(?P<tenant_id>[^/]+)/$', views.RetrieveStatus.as_view(), name='Retrieve status')
               ]
