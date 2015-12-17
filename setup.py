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
    url='https://github.com/Kortemme-Lab/rosetta_dev_tools',
    packages=[
        'rosetta_dev_tools',
    ],
    entry_points={
        'console_scripts': [
            'rdt_stub=rosetta_dev_tools.boilerplate:main',
            'rdt_build=rosetta_dev_tools.build:main',
            'rdt_unit_test=rosetta_dev_tools.unit_test:main',
            'rdt_doxygen=rosetta_dev_tools.doxygen:main',
        ],
    },
    include_package_data=True,
    install_requires=[
        'docopt==0.6.2',
        'nonstdlib>=1.5',
    ],
    license='MIT',
    zip_safe=False,
    keywords=[
        'rosetta',
        'protein',
        'design',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
    ],
)
