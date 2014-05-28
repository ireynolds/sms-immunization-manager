import os
from django.utils.translation import ugettext_lazy as _
from django.contrib.messages import constants as messages

# The top directory for this project. Contains requirements/, manage.py,
# and README.rst, a sim directory with settings etc (see
# PROJECT_PATH), as well as a directory for each Django app added to this
# project.
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

# The directory with this project's templates, settings, urls, static dir,
# wsgi.py, fixtures, etc.
PROJECT_PATH = os.path.join(PROJECT_ROOT, 'sim')

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

LANGUAGES = (
    ('en', _('English')),
    ('es', _('Spanish')),
    ('la', _('Lao')),
)

EXTRA_LANG_INFO = {
    'la': {
        'bidi': False, # left-to-right
        'code': 'la',
        'name': 'Lao',
        'name_local': u'Lao', # TODO: Insert a unicode string in Lao here, instead of an english string.
    },
}

LANGUAGE_SESSION_KEY = 'sim_language'
LANGUAGE_COOKIE_NAME = LANGUAGE_SESSION_KEY

LOCALE_PATHS = (
    os.path.join(PROJECT_PATH, 'locale'),
)

# Add custom languages not provided by Django
import django.conf.locale
LANG_INFO = dict(django.conf.locale.LANG_INFO.items() + EXTRA_LANG_INFO.items())
django.conf.locale.LANG_INFO = LANG_INFO

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/public/media/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'public', 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/public/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'public', 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files to collect
STATICFILES_DIRS = (
    os.path.join(PROJECT_PATH, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'd&x0p#ax=(3cyt(%0y^ktcd3*2^0vdlze183onz9nct#uifn*+'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.core.context_processors.i18n',
    'django.core.context_processors.static',
    'moderation.context_processors.language_name',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'moderation.middleware.SessionLanguageMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'sim.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'sim.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'templates'),
)

FIXTURE_DIRS = (
    os.path.join(PROJECT_PATH, 'fixtures'),
)

# TODO: Change these to URL pattern lookups
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

# The template pack to use with django-crispy-forms
CRISPY_TEMPLATE_PACK = 'bootstrap3'

# Define the CSS classes used to render messages
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# A sample logging configuration.
# This logs all rapidsms messages to the file `rapidsms.log`
# in the project directory.  It also sends an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'basic': {
            'format': '%(asctime)s %(name)-20s %(levelname)-8s %(message)s',
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'basic',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'basic',
            'filename': os.path.join(PROJECT_PATH, 'rapidsms.log'),
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'rapidsms': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

APPS_BEFORE_SIM = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    # External apps
    "django_nose",
    #"djtables",  # required by rapidsms.contrib.locations
    "django_tables2",
    "selectable",
    "south",
    "rapidsms.contrib.messagelog",
    "crispy_forms",
)

SIM_PRE_APPS = (
    'permissions',
    'operation_parser',
    'contextual',
)

SIM_APPS = (
    'stock',
    'equipment',
    'registration',
    'user_registration',
    'dhis2',
    'notifications',
    'utils',
    'response',
    'info'
)

APPS_AFTER_SIM = (
    'moderation',
    'reversion',

    # RapidSMS
    "rapidsms",
    "rapidsms.backends.database",
    "rapidsms.contrib.handlers",
    "rapidsms.contrib.httptester",
    "rapidsms.contrib.messaging",
)

INSTALLED_APPS = APPS_BEFORE_SIM + SIM_PRE_APPS + SIM_APPS + APPS_AFTER_SIM

INSTALLED_BACKENDS = {
    "message_tester": {
        "ENGINE": "rapidsms.backends.database.DatabaseBackend",
    },
}

RAPIDSMS_HANDLERS = (
    'rapidsms.contrib.echo.handlers.echo.EchoHandler',
    'rapidsms.contrib.echo.handlers.ping.PingHandler',
    # 'rapidsms.contrib.handlers.KeywordHandler',
    'handlers.HelpHandler',
)

# ------------------------------------------------------------------------------
# SIM-specific settings below
# ------------------------------------------------------------------------------

# Defines acceptable choices for language preference opcode
# TODO: Change language tags to something useful
PREFERRED_LANGUAGE_CODE = "[1-3]"
PREFERRED_LANGUAGES = { 1 : "English", 2 : "Karoake", 3 : "Lao" }

# Define Roles and associated string of permitted opcodes
# TODO: Require a json list of strings instead for opcodes?
DATA_REPORTER_ROLE = "DataReporter"
ADMIN_ROLE = "Admin"
ROLE_CHOICES = (
    (DATA_REPORTER_ROLE, _("Data Reporter")),
    (ADMIN_ROLE, _("Administrator"))
)

ROLE_OP_CODES = (
    (DATA_REPORTER_ROLE, ["FT", "SL", "SE", "RE", "NF", "HE", "FC"]),
    (ADMIN_ROLE, ["FT", "SL", "SE", "RE", "NF", "RG", "PL", "HE", "FC"])
)

PERIODIC = "PERIODIC"
SPONTANEOUS = "SPONTANEOUS"
ADMINISTRATION = "ADMINISTRATION"
INFORMATION = "INFORMATION"
CONTEXTUAL = "CONTEXTUAL"

SIM_OPCODE_GROUPS = {
    "FT": PERIODIC,
    "SL": PERIODIC,
    "SE": SPONTANEOUS,
    "RE": SPONTANEOUS,
    "NF": SPONTANEOUS,
    "RG": ADMINISTRATION,
    "PL": ADMINISTRATION,
    "HE": INFORMATION,
    "FC": CONTEXTUAL,
}

SIM_OPCODE_MAY_NOT_DUPLICATE = set([
    "FT",
    "SL",
    "PL",
    "HE",
    "FC"
])

# A list of AppBase subclasses that should be used by RapidSMS' router, in
# addition to those autodiscovered from INSTALLED_APPS.
# TODO: Is it possible to make these references be strings, for consistency with
# the rest of settings.py?
import stock.apps as _stock_apps
import equipment.apps as _equipment_apps
import info.apps as _info_apps
import contextual.app as _contextual_apps
import user_registration.apps as _user_registration_apps

RAPIDSMS_APP_BASES = (
    _stock_apps.StockLevel,
    _stock_apps.StockOut,
    _equipment_apps.EquipmentFailure,
    _equipment_apps.EquipmentRepaired,
    _info_apps.Help,
    _equipment_apps.FridgeTemperature,
    _user_registration_apps.PreferredLanguage,
    _user_registration_apps.UserRegistration,
)

# Configure the RapidSMS router based on RAPIDSMS_APP_BASES
from rapidsms.router.blocking import BlockingRouter
RAPIDSMS_ROUTER = BlockingRouter()
for app in RAPIDSMS_APP_BASES:
    RAPIDSMS_ROUTER.add_app(app)

# Assign operation codes to AppBase handlers.
SIM_OPERATION_CODES = {
    "SL": _stock_apps.StockLevel,
    "SE": _stock_apps.StockOut,
    "NF": _equipment_apps.EquipmentFailure,
    "RE": _equipment_apps.EquipmentRepaired,
    "HE": _info_apps.Help,
    "FT": _equipment_apps.FridgeTemperature,
    "FC": _contextual_apps.FacilityCode,
    "PL": _user_registration_apps.PreferredLanguage,
    "RG": _user_registration_apps.UserRegistration,
}
