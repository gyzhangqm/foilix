#!/usr/bin/env python
# coding: utf-8

r"""foilix's setup.py"""
import foilix
from distutils.core import setup

setup(name=foilix.__name__,
      version=foilix.__version__,
      description=foilix.__description__,
      long_description='2D foil sections simulation and optimization',
      url=foilix.__url__,
      download_url=foilix.__download_url__,
      author=foilix.__author__,
      author_email=foilix.__author_email__,
      license=foilix.__license__,
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6'],
      keywords='xfoil optimization 2d foil sections',
      packages=['foilix',
                'foilix.foil_generators',
                'examples',
                'foilix.optimization',
                'foilix.ui',
                'foilix.xfoil'],
      # install_requires=[],
      # extras_require={
      #     'dev': [],
      #     'test': ['pytest', 'coverage'],
      # },
      package_data={},
      data_files=[('foilix/xfoil',
                  ['foilix/xfoil/xfoil',
                   'foilix/xfoil/xfoil.exe'])],
      # entry_points={},
      scripts=['bin/foilix_opt_step1_data_digging.py',
               'bin/foilix_opt_step2_visual_initial_foil.py',
               'bin/foilix_opt_step3_launch_optimization.py',
               'bin/foilix_opt_step4_compare_results.py']
      )
