#!/usr/bin/env python
# coding: utf-8

r"""test xfoil.py module"""

import os

from foilix.xfoil.polar import Polar
# import foilix.xfoil.xfoil

XFOIL_EXE_TO_DAT_RELPATH = '../../foil_dat/%s'

cwd = os.getcwd()
os.chdir(os.path.join(os.path.dirname(__file__), "../../foilix/xfoil"))
xfoil_exe_dir = os.path.join(os.path.dirname(__file__), "../../foilix/xfoil")


def test_different_ncrits():
    r"""test call with different ncrits result in different values"""
    os.chdir(xfoil_exe_dir)

    foil = 's1010.dat'
    reynolds = 10000
    polar_1 = Polar("",
                    filename=XFOIL_EXE_TO_DAT_RELPATH % foil,
                    angles_of_attack_spec=[0., 10., 1.],
                    reynolds_number=reynolds,
                    ncrit=2.)
    polar_2 = Polar("",
                    filename=XFOIL_EXE_TO_DAT_RELPATH % foil,
                    angles_of_attack_spec=[0., 10., 1.],
                    reynolds_number=reynolds,
                    ncrit=3.)
    polar_1.compute()
    polar_2.compute()
    assert polar_1.max_lift_to_drag != polar_2.max_lift_to_drag
    assert polar_1.maximum_lift != polar_2.maximum_lift

    # Minimum drag seems to depend little on ncrit !
    # assert polar_1.minimum_drag != polar_2.minimum_drag

    os.chdir(cwd)


def test_same_ncrits():
    r"""Make sure calls with the same parameters have the same results
    whether using precomputed data or not"""
    os.chdir(xfoil_exe_dir)

    foil = 'naca0006.dat'
    reynolds = 10000
    polar_1 = Polar("",
                    filename=XFOIL_EXE_TO_DAT_RELPATH % foil,
                    angles_of_attack_spec=[0., 10., 1.],
                    reynolds_number=reynolds,
                    ncrit=2.,
                    use_precomputed_data=False)
    polar_2 = Polar("../../foil_data",
                    filename=XFOIL_EXE_TO_DAT_RELPATH % foil,
                    angles_of_attack_spec=[0., 10., 1.],
                    reynolds_number=reynolds,
                    ncrit=2.,
                    use_precomputed_data=True)
    print(XFOIL_EXE_TO_DAT_RELPATH % foil)
    tolerance = 1e-3
    polar_1.compute()
    polar_2.compute()
    max_lift_to_drag_value_1, max_lift_to_drag_angle_1 = \
        polar_1.max_lift_to_drag
    max_lift_to_drag_value_2, max_lift_to_drag_angle_2 = \
        polar_2.max_lift_to_drag
    assert abs(max_lift_to_drag_value_1 - max_lift_to_drag_value_2) < tolerance
    assert abs(max_lift_to_drag_angle_1 - max_lift_to_drag_angle_2) < 5e-2
    assert abs(polar_1.maximum_lift - polar_2.maximum_lift) < 1e-3
    assert abs(polar_1.minimum_drag - polar_2.minimum_drag) < 1e-5

    os.chdir(cwd)
