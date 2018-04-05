#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='yatg',
    version='0.9.2',
    author='cig01',
    author_email='juhani@163.com',
    url='https://github.com/10gic/yatg',
    description='A utility for generating ASCII art table',
    long_description=open('README.rst').read(),
    license='AGPLv3+',
    packages=['yatg'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing',
        'Topic :: Utilities',
    ],
    platforms='any',
    entry_points={'console_scripts': ['yatg=yatg:run_main']})
