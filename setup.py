#!/usr/bin/env python3
# encoding: utf-8

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import re
with open('rosetta_dev_tools/__init__.py') as file:
    version_pattern = re.compile("__version__ = '(.*)'")
    version = version_pattern.search(file.read()).group(1)

with open('README.rst') as file:
    readme = file.read()

setup(
    name='rosetta_dev_tools',
    version=version,
    author='Kale Kundert',
    author_email='kale.kundert@ucsf.edu',
    description='A set of tools to facilitate development of the Rosetta protein design suite.',
    long_description=readme,
    url='https://github.com/kalekundert/rosetta_dev_tools',
    packages=[
        'rosetta_dev_tools',
    ],
    include_package_data=True,
    install_requires=[
    ],
    license='MIT',
    zip_safe=False,
    keywords=[
        'rosetta_dev_tools',
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries',
    ],
)
