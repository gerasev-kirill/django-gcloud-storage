from setuptools import setup, find_packages
import django_gcs

setup_options = {
        'name': 'django-gcloud-storage',
        'version': django_gcs.__version__,
        'install_requires': [
            'Django>=1.10',
            'gcloud==0.18.3'
        ],

        'author': 'Colin Su',
        'author_email': 'littleq0903@gmail.com',

        'license': 'MIT',
        'description': open('./README.md').read(),
        'url': 'https://github.com/littleq0903/django-gcloud-storage',

        'classifiers': [
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Framework :: Django',
        ]
}

setup(**setup_options)
