#!/usr/bin/env python
# coding: utf-8

r"""NACA4 foil generator example"""

from __future__ import print_function
import logging
from foilix.foil_generators.naca4 import NACA4

logger = logging.getLogger(__name__)


def naca4_example():
    r"""Runs the example"""
    foil = NACA4(max_camber=0, max_camber_position=4, thickness=15)
    npts = 200

    print(foil)
    print(foil.get_coords_plain(npts))

    # write the foil coordinates to a file
    # with open("NACA0015.dat", 'w') as af:
    #     af.write("NACA 0015\n")
    #     af.write(foil.get_coords_plain(npts))

    foil.plot_foil(title="NACA %i%i%i" % (foil.max_camber*100,
                                          foil.max_camber_position*10,
                                          foil.thickness*100))

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s :: %(levelname)6s :: %(module)20s '
                               ':: %(lineno)3d :: %(message)s')
    naca4_example()
