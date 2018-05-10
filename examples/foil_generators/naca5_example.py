#!/usr/bin/env python
# coding: utf-8

r"""NACA 5 example"""

from __future__ import print_function
import logging
from foilix.foil_generators.naca5 import NACA5


def naca5_example():
    r"""Runs the example"""
    mld, t = 250, 8
    naca5_foil = NACA5(mld, t)

    # print test airfoil
    print(naca5_foil)

    # get thickness
    print("Real thickness (including camber): "
          "{:.4%}".format(naca5_foil.max_thickness()))
    print("Volume: {:.3f} chord^2".format(naca5_foil.area()))

    print(naca5_foil.get_coords_plain())
    naca5_foil.plot_foil()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s :: %(levelname)6s :: %(module)20s '
                               ':: %(lineno)3d :: %(message)s')
    naca5_example()
