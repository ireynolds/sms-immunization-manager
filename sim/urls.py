from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),

    # User auth URLs
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name="logout"),
    # TODO: Add user settings and password reset pages

    # SIM-specific URLs
    url(r'^moderation/', include('moderation.urls')),
    url(r'^$', 'moderation.views.home', name='moderation-home'),

    # RapidSMS core URLs
    url(r'^rapidsms/$', 'rapidsms.views.dashboard', name='rapidsms-dashboard'),
    url(r'^rapidsms/httptester/', include('rapidsms.contrib.httptester.urls')),
    url(r'^rapidsms/messagelog/', include('rapidsms.contrib.messagelog.urls')),
    url(r'^rapidsms/messaging/', include('rapidsms.contrib.messaging.urls')),
    url(r'^rapidsms/accounts/', include('rapidsms.urls.login_logout')),

    # Third party URLs
    url(r'^selectable/', include('selectable.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
