#!/usr/bin/python

from distutils.core import setup

setup(
    name = 'delcom904x',
    version = '0.1',
    description = 'A python class to control Delcom USBLMP Products 904x multi-color visual signal indicators',
    author = 'Aaron Linville',
    author_email = 'aaron@linville.org',
    url = 'https://github.com/linville/delcom904x',
    py_modules = ['delcom904x'],
    classifiers = [
        'Operating System :: OS Independent',
        'Topic :: System :: Hardware :: Hardware Drivers',
        'License :: OSI Approved :: ISC License (ISCL)'
    ],
    license = 'ISC',
)
