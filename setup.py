#!/usr/bin/env python
# coding: utf-8

r"""foilix's setup.py"""

from distutils.core import setup

setup(name='Foilix',
      version='0.1',
      description='2D foil sections simulation and optimization',
      author='Guillaume Florent',
      author_email='florentsailing@gmail.com',
      url='https://bitbucket.org/fullmar/foilix/',
      packages=['foilix',
                'foilix.foil_generators',
                'examples',
                'foilix.optimization',
                'foilix.ui',
                'foilix.xfoil'])
