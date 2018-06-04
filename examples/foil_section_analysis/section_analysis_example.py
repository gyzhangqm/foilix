#!/usr/bin/env python
# coding: utf-8

r"""Basic analysis"""

from __future__ import print_function

import logging
import os
import os.path

# import matplotlib
import matplotlib.pyplot as plt

# import foilix.xfoil.xfoil
from foilix.xfoil.polar import Polar


logger = logging.getLogger(__name__)


def section_analysis_example(foils_to_analyze):
    r"""Runs the example

    Parameters
    ----------
    foils_to_analyze : list[str]

    """
    # MATPLOTLIBRC = os.path.join(os.path.dirname(__file__),
    #                             'matplotlibrc_defaults')
    WORKING_DIRECTORY = os.path.join(os.path.dirname(__file__),
                                     '../../foilix/xfoil')
    XFOIL_EXE_TO_DAT_RELPATH = '../../foil_dat/%s'

    # Set the matplotlib rc_context from file
    # matplotlib.rc_context(fname=MATPLOTLIBRC)

    # Set the working directory to where the xfoil executable resides
    logger.info("Changing working directory to : %s" % WORKING_DIRECTORY)
    os.chdir(WORKING_DIRECTORY)

    # Analysis configuration
    angles_of_attack = [0, 10, 1]
    reynolds_number = 150000
    ncrit = 2.0

    foils_dat_files = [XFOIL_EXE_TO_DAT_RELPATH % f for f in foils_to_analyze]

    _, axarr = plt.subplots(2, 2)
    axarr[-1, -1].axis('off')  # hide bottom right subplot that is not used
    axarr[0, 0].set_title("Cl, Cd = f(angle)")
    axarr[0, 1].set_title("Cl = f(Cd)")
    axarr[1, 0].set_title("L/D = f(angle)")

    colors = ["red", "blue", "orange", "pink"]

    for i, dat_file in enumerate(foils_dat_files):
        # polar = foilix.xfoil.polar.Polar(foils_dat_files[0],
        #                                  angles_of_attack,
        #                                  reynolds_number,
        #                                  ncrit,
        # iterlim=100)
        polar = Polar(dat_file,
                      angles_of_attack,
                      reynolds_number,
                      ncrit,
                      iterlim=100)
        polar.compute()

        print("Max L/D : %f @ %f°" % (polar.max_lift_to_drag[0],
                                      polar.max_lift_to_drag[1]))
        print("%i angles computed out of %i "
              "specified" % (len(polar.angles_of_attack_computed),
                             len(polar.angles_of_attack_spec)))

        # Plot Cl, Cd = f(angle)
        axarr[0, 0].plot(polar.interp_aoas,
                         [polar.coefficients_of_lift_interpolator(aoa)
                          for aoa in polar.interp_aoas],
                         'r-',
                         label="%s Cl" % os.path.basename(dat_file),
                         color=colors[i])
        axarr[0, 0].scatter(polar.angles_of_attack_computed,
                            polar.coefficients_of_lift,
                            color=colors[i])
        axarr[0, 0].plot(polar.interp_aoas,
                         [polar.coefficients_of_drag_interpolator(aoa)
                          for aoa in polar.interp_aoas],
                         'r--',
                         label="%s Cd" % os.path.basename(dat_file),
                         color=colors[i])
        axarr[0, 0].scatter(polar.angles_of_attack_computed,
                            polar.coefficients_of_drag,
                            color=colors[i])
        axarr[0, 0].legend(loc="upper left")

        # Plot Cl = f(Cd)
        axarr[0, 1].plot([polar.coefficients_of_drag_interpolator(aoa)
                          for aoa in polar.interp_aoas],
                         [polar.coefficients_of_lift_interpolator(aoa)
                          for aoa in polar.interp_aoas],
                         'r-',
                         label="%s Cl" % os.path.basename(dat_file),
                         color=colors[i])
        axarr[0, 1].scatter(polar.coefficients_of_drag,
                            polar.coefficients_of_lift,
                            color=colors[i])

        # Plot L/D = f(aoa)

        axarr[1, 0].plot(polar.interp_aoas,
                         [polar.lift_to_drag_interpolator(aoa)
                          for aoa in polar.interp_aoas],
                         'r-',
                         label="%s L/D" % os.path.basename(dat_file),
                         color=colors[i])
        axarr[1, 0].scatter(polar.angles_of_attack_computed,
                            polar.lift_to_drag,
                            color=colors[i])

    plt.gcf().suptitle(str("%s reynolds; %s ncrit" % (str(reynolds_number),
                                                      str(ncrit))))
    plt.show()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s :: %(levelname)6s :: %(module)20s '
                               ':: %(lineno)3d :: %(message)s')
    # Foils to analyze (s1010: Max thickness 6% at 23.3% chord.,
    # naca0006: Max thickness 6% at 30% chord.)
    section_analysis_example(foils_to_analyze=['naca0006.dat',
                                               's1010.dat',
                                               'naca0005.dat'])
