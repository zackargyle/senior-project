from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('backend.views',
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^$', TemplateView.as_view(template_name='homepage.html'), name="home"),
                       url(r'^', include('api.urls')))
