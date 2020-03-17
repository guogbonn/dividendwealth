from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']#'127.0.0.1'

# INSTALLED_APPS += [
#     'debug_toolbar',
#     'template_timings_panel',
#
# ]
#
# MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware',]
#
# # DEBUG TOOLBAR SETTINGS
#
# DEBUG_TOOLBAR_PANELS = [
#     'debug_toolbar.panels.versions.VersionsPanel',
#     'debug_toolbar.panels.timer.TimerPanel',
#     'debug_toolbar.panels.settings.SettingsPanel',
#     'debug_toolbar.panels.headers.HeadersPanel',
#     'debug_toolbar.panels.request.RequestPanel',
#     'debug_toolbar.panels.sql.SQLPanel',
#     'debug_toolbar.panels.staticfiles.StaticFilesPanel',
#     'debug_toolbar.panels.templates.TemplatesPanel',
#     'debug_toolbar.panels.cache.CachePanel',
#     'debug_toolbar.panels.signals.SignalsPanel',
#     'debug_toolbar.panels.logging.LoggingPanel',
#     'debug_toolbar.panels.redirects.RedirectsPanel',
#     #Template-timings is a panel for Django Debug Toolbar that gives an in-dept breakdown of the time it takes to render your Django templates (including templates included via
#     #https://github.com/orf/django-debug-toolbar-template-timings
#     'template_timings_panel.panels.TemplateTimings.TemplateTimings',
# ]
#
# def show_toolbar(request):
#     return True
#
# DEBUG_TOOLBAR_CONFIG = {
#     'INTERCEPT_REDIRECTS': False,
#     'SHOW_TOOLBAR_CALLBACK': show_toolbar
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

STRIPE_PUBLIC_KEY = 'pk_test_WE1TeLiXSpVL9yqpSrL7nheS00ffFJO2uH'
STRIPE_SECRET_KEY = 'sk_test_6oPwZEN9U7Xa8oLdkOEeixxr00iUbx4qJ0'
CLIENT_ID='ca_GO02Bv8oarPFwOTBC1NpCA362GPwR1oN'
