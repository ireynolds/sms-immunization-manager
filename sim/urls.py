from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    # RapidSMS core URLs
    url(r'^rapidsms/$', 'rapidsms.views.dashboard', name='rapidsms-dashboard'),
    (r'^rapidsms/httptester/', include('rapidsms.contrib.httptester.urls')),
    (r'^rapidsms/messagelog/', include('rapidsms.contrib.messagelog.urls')),
    (r'^rapidsms/messaging/', include('rapidsms.contrib.messaging.urls')),

    # Third party URLs
    (r'^selectable/', include('selectable.urls')),
    (r'^moderation/', include('moderation.urls')),
    url(r'^$', 'moderation.views.home', name='moderation-home'),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
