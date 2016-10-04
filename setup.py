#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
from setuptools import setup, find_packages


with open('secure_redis/__init__.py', 'r') as init_file:
    version = re.search(
        '^__version__ = [\'"]([^\'"]+)[\'"]',
        init_file.read(),
        re.MULTILINE,
    ).group(1)

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-redis-secure',
    version=version,
    packages=find_packages(),
    license='MIT',
    include_package_data=True,
    description=(
        'Django caching plugin for django-redis that adds a Serializer class and configuration to support '
        'transparent, symmetrical encryption of cached values using the python cryptography library. This '
        'plugin also provides encryption for django-rq jobs by simply using the @secure_redis.secure_rq.job '
        'decorator to annotate the task method instead of using @django_rq.job.'
    ),
    url='http://github.com/foundertherapy/django-redis-secure/',
    download_url='https://github.com/foundertherapy/django-redis-secure/archive/' + version + '.tar.gz',
    author='FounderTherapy',
    author_email='oss@foundertherapy.com',
    install_requires=[
        'Django>=1.9',
        'cryptography>=0.8.2',
        'django-rq>=0.9.1',
        'rq>=0.6.0',
        'rq-scheduler>=0.6.1',
        'django-redis',
    ],
    keywords=['encryption', 'django', 'redis', 'rq', ],
)
