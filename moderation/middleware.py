from django.conf import settings
from django.utils import translation

class SessionLanguageMiddleware(object):
    """
    This middleware updates the current language based on a session token.
    Based on django.middleware.locale.LocaleMiddleware in Django 1.7.
    """

    def process_request(self, request):
        if (hasattr(request, 'session') and 
            settings.LANGUAGE_SESSION_KEY in request.session):

            language = request.session[settings.LANGUAGE_SESSION_KEY]

            if translation.check_for_language(language):
                translation.activate(language)
                request.LANGUAGE_CODE = translation.get_language()