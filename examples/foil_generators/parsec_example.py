#!/usr/bin/env python
# coding: utf-8

r"""PARSEC foil generator example"""

from __future__ import print_function

import logging

from foilix.foil_generators.parsec import PARSEC


def assymmetrical_foil_section():
    r"""Assymmetrical PARSEC foil section"""
    k = {'rle': .01,
         'x_pre': .45,
         'y_pre': -0.006,
         'd2ydx2_pre': -.2,
         'th_pre': 2,
         'x_suc': .35,
         'y_suc': .055,
         'd2ydx2_suc': -.35,
         'th_suc': -10,
         'xte': 1.0,
         'yte': -0.05}

    foil = PARSEC(k)
    print(foil)
    print(foil.get_coords_plain())
    foil.plot_foil("PARSEC")


def symmetrical_foil_section():
    r"""Symmetrical PARSEC foil section"""
    x = 0.25
    y = 0.03
    d2ydx2 = 0.25
    th = 6.
    k = {'rle': .005,
         'x_pre': x,
         'y_pre': -y,
         'd2ydx2_pre': d2ydx2,
         'th_pre': th,
         'x_suc': x,
         'y_suc': y,
         'd2ydx2_suc': -d2ydx2,
         'th_suc': -th,
         'xte': 1.,
         'yte': 0.}

    foil = PARSEC(k)
    print(foil)
    print(foil.get_coords_plain())
    foil.plot_foil("PARSEC-SYMMETRICAL")


def symmetrical_foil_section_invalid():
    r"""Symmetrical PARSEC foil section but invalid"""
    x = 0.25
    y = 0.03
    d2ydx2 = 0.47
    th = 6.
    k = {'rle': .005,
         'x_pre': x,
         'y_pre': -y,
         'd2ydx2_pre': d2ydx2,
         'th_pre': th,
         'x_suc': x,
         'y_suc': y,
         'd2ydx2_suc': -d2ydx2,
         'th_suc': -th,
         'xte': 1.,
         'yte': 0.}

    foil = PARSEC(k)
    print(foil)
    print(foil.get_coords_plain())
    foil.plot_foil("PARSEC-SYMMETRICAL-INVALID")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s :: %(levelname)6s :: %(module)20s '
                               ':: %(lineno)3d :: %(message)s')
    assymmetrical_foil_section()
    symmetrical_foil_section()
    symmetrical_foil_section_invalid()
