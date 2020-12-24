#!/usr/bin/env python3

from setuptools import find_packages, setup

INSTALL_REQUIRES = ['numpy', 'pandas', 'scipy']
TESTS_REQUIRE = ['pytest >= 2.7.1']

setup(
    name='rec_to_binaries',
    version='0.6.2.dev0',
    license='MIT',
    description=('Covert SpikeGadgets rec files to binaries'),
    author='Eric Denovellis, Daniel Liu',
    author_email='Eric.Denovellis@ucsf.edu',
    url='https://github.com/LorenFrankLab/rec_to_binaries',
    packages=find_packages(),
    install_requires=INSTALL_REQUIRES,
    python_requires='>=3.6',
    tests_require=TESTS_REQUIRE,
)
