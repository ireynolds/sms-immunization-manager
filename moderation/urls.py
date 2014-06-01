from django.conf.urls import patterns, include, url

urlpatterns = patterns('moderation.views',
    url(r'^$', 'home'),
    url(r'^node/$', 'root_nodes'),
    url(r'^node/(\d+)/$', 'node'),

    url(r'^facility/(\d+)/$', 'facility'),

    url(r'^contact/(\d+)/$', 'contact'),
    url(r'^contact/(\d+)/edit/$', 'contact_edit'),

    url(r'^effect/(\d+)/dismiss/$', 'effect_dismiss', {"dismiss_value": True}, name="dismiss"),
    url(r'^effect/(\d+)/undismiss/$', 'effect_dismiss', {"dismiss_value": False}, name="undismiss"),
    url(r'^message/(\d+)/dismiss/$', 'message_dismiss'),
    url(r'^contact/(\d+)/dismiss/$', 'contact_dismiss'),

    url(r'^set_language/$', 'set_language', name="set_language"),
    url(r'^set_default_language/$', 'set_default_language', name="set_default_language"),
    url(r'^set_affiliation/$', 'set_affiliation', name="set_affiliation"),
)