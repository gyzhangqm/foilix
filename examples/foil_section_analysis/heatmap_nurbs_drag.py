#!/usr/bin/python
# coding: utf-8

r"""An example to show how to combine NURBS airfoil_generator and XFOIL"""

from __future__ import print_function

import logging
import matplotlib.pyplot as plt
import numpy as np
import os

from foilix.foil_generators.nurbs import NURBS
from foilix.xfoil.xfoil import oper_visc_cl


def example_nurbs_drag():
    r"""Example Nurbs foils drag analysis"""
    reynolds = 100000
    Cl = 0.2

    drags = np.zeros((5, 3))

    tb_u = np.linspace(1.8, 2.2, 6)
    alpha_b = np.linspace(11.1, 12, 4)

    for i in range(1, 6):
        for j in range(1, 4):
            # make new airfoil
            k = dict()
            k['ta_u'] = 0.1584
            k['ta_l'] = 0.1565
            k['tb_u'] = tb_u[i]
            k['tb_l'] = 1.8255
            k['alpha_b'] = alpha_b[j]
            k['alpha_c'] = 3.8270
            nurbs_foil = NURBS(k)

            # make unique filename
            temp_af_filename = "temp_airfoil_{}{}.dat".format(i, j)

            # Save coordinates
            with open(temp_af_filename, 'w') as nurbs_foil_file:
                nurbs_foil_file.write(nurbs_foil.get_coords_plain())

            # Let Xfoil do its thing
            polar = oper_visc_cl(temp_af_filename, Cl, reynolds, iterlim=1000)

            # Save Cd
            try:
                drags[i-1][j-1] = polar[0][0][2]
            except IndexError:
                raise Warning("Shit! XFOIL didn't converge on NACA{}{}15 at "
                              "Cl={}.".format(i, j, Cl))

            yu, xu, yl, xl,  = nurbs_foil.get_coords()

            def translated_plt(x, y, *args):
                r"""Translated plot

                Parameters
                ----------
                x
                y

                """
                plt.plot(x * 0.8 + (j - .9), y * 0.8 + (i - 0.5), *args)

            translated_plt(yl, xl, 'w')
            translated_plt(yu, xu, 'w')

            os.remove(temp_af_filename)

    print(drags)

    plt.pcolor(drags, cmap=plt.cm.RdBu)
    plt.pcolor(drags, cmap=plt.cm.coolwarm)

    cbar = plt.colorbar()
    cbar.ax.set_ylabel("Drag coefficient $C_d$")
    plt.yticks((.5, 1.5, 2.5, 3.5, 4.5), ("1", "2", "3", "4", "5"))
    plt.xticks((.5, 1.5, 2.5), ("1", "2", "3"))
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s :: %(levelname)6s :: %(module)20s '
                               ':: %(lineno)3d :: %(message)s')
    example_nurbs_drag()
