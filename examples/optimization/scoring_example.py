#!/usr/bin/env python
# coding: utf-8

r"""Scoring example"""

from __future__ import print_function

import logging

from foilix.xfoil.polar import PolarMatrix
from foilix.optimization.scoring import compound_score


def scoring_example():
    r"""Runs the example"""
    XFOIL_EXE_TO_DAT_RELPATH = '../../foil_dat/%s'

    # Define an XFoilPilot over a list of Reynolds
    # and for a range of angles of attack
    polar_matrix = PolarMatrix(XFOIL_EXE_TO_DAT_RELPATH % "s1010.dat",
                               [0, 20, 0.5],
                               [5E4, 1E5],
                               ncrits=[2.0],
                               iterlim=500)
    polar_matrix.compute()

    print("Score : %f" % compound_score(polar_matrix.avg_max_lift[0],
                                        polar_matrix.avg_min_drag[0],
                                        polar_matrix.avg_max_lift_to_drag[0]))

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s :: %(levelname)6s :: %(module)20s '
                               ':: %(lineno)3d :: %(message)s')
    scoring_example()
