#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
from setuptools import setup, find_packages


with open('secure_redis/__init__.py', 'r') as init_file:
    version = re.search('^__version__ = [\'"]([^\'"]+)[\'"]', init_file.read(), re.MULTILINE).group(1)

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-redis-secure',
    version=version,
    packages=find_packages(),
    # license='MIT License',
    # include_package_data=True,
    description=(
        'Django caching plugin for django-redis that adds a Serializer class and configuration to support transparent, '
        'symmetrical encryption of cached values using the python cryptography library'
    ),
    url='https://github.com/foundertherapy/django-redis-secure/',
    download_url='https://github.com/foundertherapy/django-redis-secure/archive/1.0.1.tar.gz',
    author='Ghaleb Khaled',
    author_email='ghaleb@foundertherapy.co',
    install_requires=[
        'Django>=1.9.6',
        'cryptography>=1.4',
        'django-redis==4.4.3',
        'django-rq==0.9.1',
        'rq==0.6.0',
        'rq-scheduler==0.6.1',
    ],
    keywords=['redis', 'django', 'secure', 'encryption', 'cache', 'rq', 'queue', 'scheduler'],
)
