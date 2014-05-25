from django.conf.urls import patterns, include, url

urlpatterns = patterns('moderation.views',
    url(r'^$', 'home'),
    url(r'^node/$', 'root_nodes'),
    url(r'^node/(\d+)/$', 'node'),

    url(r'^facility/(\d+)/$', 'facility'),

    url(r'^user/(\d+)/$', 'user_summary'),
    url(r'^user/(\d+)/edit/$', 'user_edit'),

    url(r'^set_language/$', 'set_language', name="set_language"),
    url(r'^set_default_language/$', 'set_default_language', name="set_default_language"),
    url(r'^set_affiliation/$', 'set_affiliation', name="set_affiliation"),
)