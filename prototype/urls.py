from django.conf.urls import patterns, include, url

urlpatterns = patterns('prototype.views',
    url(r'^$', 'facility_list'),
    url(r'^facility/(\d+)/$', 'facility'),
    url(r'^user/(\d+)/$', 'user'),
)