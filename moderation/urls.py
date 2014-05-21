from django.conf.urls import patterns, include, url

urlpatterns = patterns('moderation.views',
    url(r'^$', 'home'),
    url(r'^node/$', 'root_nodes'),
    url(r'^node/(\d+)/$', 'node'),

    url(r'^facility/(\d+)/$', 'facility'),

    url(r'^user/(\d+)/$', 'user_summary'),
    url(r'^user/(\d+)/edit/$', 'user_edit'),
)