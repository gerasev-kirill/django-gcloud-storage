import sys
import os
import django

from django.conf import settings
from django.core.management import call_command



BASE_DIR = os.path.dirname(os.path.abspath(__file__))


try:
    test_settings = {
        'DEBUG': True,

        'DATABASES': {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': os.path.join(BASE_DIR, 'test.db'),
            }
        },

        'INSTALLED_APPS': [
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sites",
            "test_app"
        ],

        'SITE_ID': 1,
        'NOSE_ARGS': ['-s'],
        'DEFAULT_FILE_STORAGE': 'django_gcs.storage.GoogleCloudStorage',

        'CACHES': {
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            }
        }
    }

except ImportError:
    raise ImportError('run `pip install -r requirements_test.txt to install testing dependencies.')

import test_secrets


gcs_settings = {
    'DJANGO_GCS_BUCKET': getattr(test_secrets, 'DJANGO_GCS_BUCKET', None),
    'DJANGO_GCS_PRIVATE_KEY_PATH': getattr(test_secrets, 'DJANGO_GCS_PRIVATE_KEY_PATH', None)
}


all_settings = {}
all_settings.update(test_settings)
all_settings.update(gcs_settings)

settings.configure(**all_settings)




if django.VERSION[0] == 1 and django.VERSION[1] <= 8:
    call_command('syncdb', migrate=True)
    from django.test.simple import DjangoTestSuiteRunner
    test_runner = DjangoTestSuiteRunner(verbosity=1)
else:
    django.setup()
    call_command('migrate', migrate=True)
    from django.test.runner import DiscoverRunner
    test_runner = DiscoverRunner(verbosity=1)



failures = test_runner.run_tests(['tests'])
if failures:
    sys.exit(failures)
