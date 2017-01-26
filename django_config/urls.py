from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^docs/', include('rest_framework_swagger.urls')),
                       url(r'^config/', include('configuration_service_core.rest_interface.urls')),
                       )

urlpatterns += staticfiles_urlpatterns()
