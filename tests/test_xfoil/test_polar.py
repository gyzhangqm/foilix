#!/usr/bin/env python
# coding: utf-8

r"""Tests for the foilix.xfoil.polar module"""

import os

from foilix.xfoil.polar import Polar, PolarMatrix
# import foilix.xfoil.xfoil

XFOIL_EXE_TO_DAT_RELPATH = '../../foil_dat/%s'

cwd = os.getcwd()
os.chdir(os.path.join(os.path.dirname(__file__), "../../foilix/xfoil"))
xfoil_exe_dir = os.path.join(os.path.dirname(__file__), "../../foilix/xfoil")


def test_expected_values_every_degree():
    r"""Test against expected values"""
    os.chdir(xfoil_exe_dir)

    foil = 's1010.dat'
    reynolds = 10000
    polar = Polar(foil_data_folder=None,
                  filename=XFOIL_EXE_TO_DAT_RELPATH % foil,
                  angles_of_attack_spec=[0., 10., 1.],
                  reynolds_number=reynolds,
                  ncrit=2.,
                  iterlim=200,
                  use_precomputed_data=False)
    polar.compute()
    tolerance_default = 1e-5
    max_lift_to_drag_value, max_lift_to_drag_angle = polar.max_lift_to_drag
    max_lift_value, max_lift_angle = polar.maximum_lift
    min_drag_value, min_drag_angle = polar.minimum_drag
    assert abs(max_lift_to_drag_value - 10.534996828082047) < 1e-2
    assert abs(max_lift_to_drag_angle - 5.) < tolerance_default
    assert abs(max_lift_value - 0.66110000000000002) < 1e-3

    # Due to interpolation (PChip), the max lift angle lies at one of the
    # computed angles
    assert abs(max_lift_angle - 9.) < tolerance_default

    assert abs(min_drag_value - 0.032079999999999997) < 1e-4
    assert abs(min_drag_angle) < tolerance_default

    os.chdir(cwd)


def test_expected_values_every_tenth_of_a_degree():
    r"""Test against expected values"""
    os.chdir(xfoil_exe_dir)

    foil = 's1010.dat'
    reynolds = 10000
    # Compute every tenth of degree
    polar = Polar(foil_data_folder=None,
                  filename=XFOIL_EXE_TO_DAT_RELPATH % foil,
                  angles_of_attack_spec=[0., 10., 0.1],
                  reynolds_number=reynolds,
                  ncrit=2.,
                  iterlim=200,
                  use_precomputed_data=False)
    polar.compute()
    tolerance_default = 1e-5
    max_lift_to_drag_value, max_lift_to_drag_angle = polar.max_lift_to_drag
    max_lift_value, max_lift_angle = polar.maximum_lift
    min_drag_value, min_drag_angle = polar.minimum_drag
    assert abs(max_lift_to_drag_value - 10.540968764146672) < tolerance_default
    assert abs(max_lift_to_drag_angle - 4.6) < tolerance_default
    assert abs(max_lift_value - 0.66379999999999995) < 1e-3

    # Due to interpolation (PChip), the max lift angle lies at one of the
    # computed angles
    assert abs(max_lift_angle - 9.1) < tolerance_default

    assert abs(min_drag_value - 0.032079999999999997) < tolerance_default

    # Minimum drag may occur close to but not at 0 degree
    assert abs(min_drag_angle) < 0.1 + tolerance_default

    os.chdir(cwd)


def test_polar_vs_polar_matrix():
    r"""A matrix is made using 3 times the same reynolds number
    and twice the same ncrit

    The averaged results of the matrix should be the same as the results
    of a polar for the same reynolds and ncrit

    """
    os.chdir(xfoil_exe_dir)

    foil = 's1010.dat'
    aos_spec = [0., 10., 1.]
    reynolds = 10000
    ncrit = 2.
    polar = Polar("",
                  filename=XFOIL_EXE_TO_DAT_RELPATH % foil,
                  angles_of_attack_spec=aos_spec,
                  reynolds_number=reynolds, ncrit=ncrit)
    polar_matrix = PolarMatrix("",
                               filename=XFOIL_EXE_TO_DAT_RELPATH % foil,
                               angles_of_attack_spec=aos_spec,
                               reynolds_numbers=[reynolds, reynolds, reynolds],
                               ncrits=[ncrit, ncrit])
    polar.compute()
    polar_matrix.compute()

    tolerance = 1e-5

    polar_max_lift_to_drag_value, polar_max_lift_to_drag_angle = \
        polar.max_lift_to_drag
    polar_matrix_max_lift_to_drag_value, polar_matrix_max_lift_to_drag_angle = \
        polar_matrix.avg_max_lift_to_drag
    assert abs(polar_max_lift_to_drag_value - polar_matrix_max_lift_to_drag_value) < tolerance
    assert abs(polar_max_lift_to_drag_angle - polar_matrix_max_lift_to_drag_angle) < tolerance

    polar_max_lift_value, polar_max_lift_angle = polar.maximum_lift
    polar_matrix_max_lift_value, polar_matrix_max_lift_angle = \
        polar_matrix.avg_max_lift
    assert abs(polar_max_lift_value - polar_matrix_max_lift_value) < tolerance
    assert abs(polar_max_lift_angle - polar_matrix_max_lift_angle) < tolerance

    polar_min_drag_value, polar_min_drag_angle = polar.minimum_drag
    polar_matrix_min_drag_value, polar_matrix_min_drag_angle = \
        polar_matrix.avg_min_drag
    assert abs(polar_min_drag_value - polar_matrix_min_drag_value) < tolerance
    assert abs(polar_min_drag_angle - polar_matrix_min_drag_angle) < tolerance

    os.chdir(cwd)
