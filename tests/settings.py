"""
Django settings for tests of the django-flexquery project.
"""

SECRET_KEY = "om-l3b3%$jutfygk%pyg#i0hp@g$v4b=-jcsa_)+%^7nig@up4"
DEBUG = True
INSTALLED_APPS = ["django_flexquery_tests"]
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
