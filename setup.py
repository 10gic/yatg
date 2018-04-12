#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup

base_dir = os.path.dirname(__file__)

author = email = source = version = None
with open(os.path.join(base_dir, "yatg", "yatg.py")) as f:
    for line in f:
        if line.strip().startswith('__version__'):
            version = line.split('=')[1].strip().replace('"', '').replace(
                "'", '')
        elif line.strip().startswith('__author__'):
            author = line.split('=')[1].strip().replace('"', '').replace(
                "'", '')
        elif line.strip().startswith('__email__'):
            email = line.split('=')[1].strip().replace('"', '').replace(
                "'", '')
        elif line.strip().startswith('__source__'):
            source = line.split('=')[1].strip().replace('"', '').replace(
                "'", '')
        elif None not in (version, author, email, source):
            break

setup(
    name='yatg',
    version=version,
    author=author,
    author_email=email,
    url=source,
    license='AGPLv3+',
    description='A utility for generating ASCII art table',
    long_description=open('README.rst').read(),
    packages=['yatg'],
    extras_require={
        'forcewidth1': ["emoji"],
        'alignintty': ["blessed"]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing',
        'Topic :: Utilities',
    ],
    platforms='any',
    entry_points={'console_scripts': ['yatg=yatg:run_main']})
