#!/usr/bin/env python3

import setuptools

setuptools.setup(
        name = "rosetta_dev_tools",
        description = "A set of tools to facilitate development of the Rosetta protein design suite.",
        long_description = open("README.rst").read(),
        url = 'https://github.com/Kortemme-Lab/rosetta_dev_tools',
        author = "Kale Kundert",
        author_email = 'kale.kundert@ucsf.edu',
        version = "0.0",
        packages = [
            'rosetta_dev_tools',
        ],
        install_requires=[
            'docopt==0.6.2',
        ],
        entry_points = {
            'console_scripts': [
                'rdt_build=rosetta_dev_tools.build:main',
                'rdt_unit_test=rosetta_dev_tools.unit_test:main',
                'rdt_doxygen=rosetta_dev_tools.doxygen:main',
            ],
        }
)



