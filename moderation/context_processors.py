from django.conf import settings
from django.utils import translation

def language_name(request):
    """
    Adds a context key LANGUAGE_NAME that contains the localed name of the current language.
    """
    context_extras = {}
    context_extras["LANGUAGE_NAME"] = dict(settings.LANGUAGES)[translation.get_language()]

    return context_extras