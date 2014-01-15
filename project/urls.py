from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

from project import views

urlpatterns = patterns('backend.views',
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^$', views.index, name='home'),
                       url(r'^review/(?P<pk>[0-9]+)$', views.review, name='review'),
                       url(r'^', include('api.urls')))
