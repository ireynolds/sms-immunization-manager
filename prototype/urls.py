from django.conf.urls import patterns, include, url

urlpatterns = patterns('prototype.views',
    url(r'^$', 'home'),
    url(r'^node/(\d+)/$', 'node'),
    url(r'^message/(\d+)/$', 'message'),
    url(r'^user/(\d+)/$', 'user'),
)