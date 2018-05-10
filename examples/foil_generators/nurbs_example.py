#!/usr/bin/env python
# coding: utf-8

r"""Nurbs foil parameterization example"""

from __future__ import print_function
import logging
from foilix.foil_generators.nurbs import NURBS


def nurbs_example():
    r"""Runs an example'''"""
    k = dict()
    # sample coefficients: Coefficients for generating NACA5410
    k['ta_u'] = 0.15
    k['ta_l'] = 0.09
    k['tb_u'] = 2.9
    k['tb_l'] = 2.9
    k['alpha_b'] = 6
    k['alpha_c'] = -1.

    nurbs_foil = NURBS(k)
    print(nurbs_foil)
    print(nurbs_foil.get_coords_plain())
    nurbs_foil.plot_foil(title="NURBS")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s :: %(levelname)6s :: %(module)20s '
                               ':: %(lineno)3d :: %(message)s')
    nurbs_example()
