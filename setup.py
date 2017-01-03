import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-gcloud-storage',
    version='0.22.0',
    packages=['django_gcs'],
    include_package_data=True,
    license='MIT License',
    description='Google Cloud Storage for Django',
    long_description=README,
    author='Colin Su<littleq0903@gmail.com>, Gerasev Kirill',
    author_email='gerasev.kirill@gmail.com',
    install_requires=[
        'Django>=1.10',
        'google-cloud==0.22.0'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
)
