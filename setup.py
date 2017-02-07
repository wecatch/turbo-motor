#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    'pymongo>=3.2',
    'motor==1.1',
    'turbo>=0.4.5'
]


setup(
    name='turbo_motor',
    version='0.0.3',
    description="Turbo motor plugin",
    long_description=readme + '\n\n' + history,
    author="zhyq0826",
    author_email='wecatch.me@gmail.com',
    url='https://github.com/wecatch/turbo-motor',
    packages=[
        'turbo_motor',
    ],
    package_dir={'turbo_motor':
                 'turbo_motor'},
    include_package_data=True,
    install_requires=requirements,
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords='turbo_motor,turbo',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ]
)
