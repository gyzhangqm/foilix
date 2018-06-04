#!/usr/bin/env python
# coding: utf-8

r"""Basic analysis"""

from __future__ import print_function

import logging
import os
import os.path

import matplotlib

from corelib.core.files import p_

from foilix.xfoil.polar import PolarMatrix


logger = logging.getLogger(__name__)


def matrix_section_analysis_example():
    r"""Runs the example"""

    MATPLOTLIBRC = p_(__file__, 'matplotlibrc_defaults')
    WORKING_DIRECTORY = p_(__file__, '../../foilix/xfoil')
    XFOIL_EXE_TO_DAT_RELPATH = '../../foil_dat/%s'

    # Set the matplotlib rc_context from file
    matplotlib.rc_context(fname=MATPLOTLIBRC)

    # Set the working directory to where the xfoil executable resides
    logger.info("Changing working directory to : %s" % WORKING_DIRECTORY)
    os.chdir(WORKING_DIRECTORY)

    # Analysis configuration
    angles_of_attack = [0, 10, 1]
    # reynolds_numbers = [10000, 150000, 300000]
    # ncrits = [2.0, 3.0]
    reynolds_numbers = [25e3, 40e3, 45e3, 50e3]
    ncrits = [1.0, 1.5, 2.0]

    # Foils to analyze (s1010: Max thickness 6% at 23.3% chord.,
    #                   naca0006: Max thickness 6% at 30% chord.)
    foils_dat_files = [XFOIL_EXE_TO_DAT_RELPATH % f for f in ['naca0006.dat']]

    polar_matrix = PolarMatrix(foil_data_folder="../../foil_data",
                               filename=os.path.basename(foils_dat_files[0]),
                               angles_of_attack_spec=angles_of_attack,
                               reynolds_numbers=reynolds_numbers,
                               ncrits=ncrits,
                               iterlim=100,
                               use_precomputed_data=True)
    polar_matrix.compute()

    print("Avg Max L/D : %f @ %f°" % (polar_matrix.avg_max_lift_to_drag[0],
                                      polar_matrix.avg_max_lift_to_drag[1]))
    print("Avg Max L : %f @ %f°" % (polar_matrix.avg_max_lift[0],
                                    polar_matrix.avg_max_lift[1]))
    print("Avg Min D : %f @ %f°" % (polar_matrix.avg_min_drag[0],
                                    polar_matrix.avg_min_drag[1]))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s :: %(levelname)6s :: %(module)20s '
                               ':: %(lineno)3d :: %(message)s')
    matrix_section_analysis_example()
