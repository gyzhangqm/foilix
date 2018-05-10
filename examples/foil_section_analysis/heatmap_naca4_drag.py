#!/usr/bin/python
# coding: utf-8

r"""Combining a NACA4 airfoil generator and XFOIL to graph the drag of foils"""

from __future__ import print_function

import logging
import os

import matplotlib.pyplot as plt
import numpy as np

from foilix.foil_generators.naca4 import NACA4
from foilix.xfoil.xfoil import oper_visc_cl


def naca4_drag_example():
    r"""Runs the example"""
    # Operating point
    Re = 1000000  # 1 million
    Cl = .4

    drags = np.zeros(shape=(5, 3))  # 5 lines, 3 columns in the final graph

    # Python 3 range is Python 2's xrange
    # (minimal impact of using range in Python 2)
    for camber in range(1, 6):  # camber in percent (5 values)

        # position of max. camber in tenths (3 values)
        for position_of_max_camber in range(4, 7):

            # Make new airfoil NACAmp15
            airfoil = NACA4(camber, position_of_max_camber, 15)

            # Make unique filename
            temp_af_filename = "temp_airfoil" \
                               "_{}{}.dat".format(camber,
                                                  position_of_max_camber)

            with open(temp_af_filename, 'w') as af:
                af.write(airfoil.get_coords_plain())  # Save coordinates

            # Let XFOIL do its thing
            polar = oper_visc_cl(temp_af_filename, Cl, Re, iterlim=500)

            try:
                # Save Cd
                drags[camber-1][position_of_max_camber-4] = polar[0][0][2]
            except IndexError:
                import warnings
                # raise Warning("XFOIL didn't converge on NACA%i%i15 "
                #               "at Cl=%f." % (camber,
                #                              position_of_max_camber,
                #                              Cl))
                warnings.warn("XFOIL didn't converge on NACA%i%i15 "
                              "at Cl=%f." % (camber,
                                             position_of_max_camber,
                                             Cl))

            xl, yl, xu, yu, xc, yc = airfoil.get_coords()  # Plot airfoil shape

            def translated_plt(x, y, *args):
                r"""Translated plot

                Parameters
                ----------
                x
                y

                """
                plt.plot(x * .8 + (position_of_max_camber - 3.9),
                         y * .8 + (camber - .5), *args)

            translated_plt(xl, yl, 'w')
            translated_plt(xu, yu, 'w')
            translated_plt(xc, yc, 'w--')

            os.remove(temp_af_filename)  # Remove temporary file

    plt.pcolor(drags, cmap=plt.cm.coolwarm)  # Plot drag values in color

    # Make plot pretty
    plt.title(r"$C_d$ of $NACAmp15$ at $C_l={}$ and $Re={:g}$".format(Cl, Re))
    plt.xlabel("Location of max. camber $p$")
    plt.ylabel("Max. camber $m$")
    cbar = plt.colorbar()
    cbar.ax.set_ylabel("Drag coefficient $C_d$")
    plt.yticks((.5, 1.5, 2.5, 3.5, 4.5),
               ("1p15", "2p15", "3p15", "4p15", "5p15"))
    plt.xticks((.5, 1.5, 2.5), ("m415", "m515", "m615"))
    plt.tight_layout()

    plt.show()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s :: %(levelname)6s :: %(module)20s '
                               ':: %(lineno)3d :: %(message)s')
    naca4_drag_example()
