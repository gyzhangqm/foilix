#!/usr/bin/env python
# coding: utf-8

r"""Rank symmetrical foil in foil_dat according to max_thickness_x

This script creates Foil objects using the dat file in foil_dat
The Foil objects are then ranked according to their max_thickness_x

"""
from __future__ import print_function
import logging
import os

import foilix.foil


def foil_order_by_thickness():
    r"""Runs the example"""
    symmetrical_foil_and_max_thickness_list = list()
    symmetrical_foil_and_max_thickness_position_list = list()

    for foil_dat_file in os.listdir("../../foil_dat/"):
        path = os.path.join(os.path.dirname(__file__), "../../foil_dat/")
        filepath = os.path.join(path, foil_dat_file)
        foil = foilix.foil.Foil.from_dat_file(filepath)
        if foil.is_symmetrical():
            try:
                symmetrical_foil_and_max_thickness_list.append((foil.name,
                                                                foil.y_spread))
                symmetrical_foil_and_max_thickness_position_list.append((foil.name,
                                                                         foil.max_y_x))
            except ValueError:
                print("Value Error for %s" % foil.name)

    # Sort

    # sort by ascending thickness
    symmetrical_foil_and_max_thickness_list.sort(key=lambda x: x[1])

    # sort by ascending thickness position
    symmetrical_foil_and_max_thickness_position_list.sort(key=lambda x: x[1])

    # print(symmetrical_foil_and_max_thickness_position_list)

    for e in symmetrical_foil_and_max_thickness_list:
        print(e)
    print(60*"*")
    for e in symmetrical_foil_and_max_thickness_position_list:
        print(e)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s :: %(levelname)6s :: %(module)20s '
                               ':: %(lineno)3d :: %(message)s')
    foil_order_by_thickness()
