#!/usr/bin/env python
# coding: utf-8

r"""NURBS foil generator tests"""

from __future__ import division, print_function

import pytest

from foilix.foil_generators.nurbs import NURBS


@pytest.mark.parametrize("ta_u, ta_l, tb_u, tb_l, alpha_b, alpha_c,"
                         "is_symmetrical_value",
                         [(1., 1., 2., 2., 6., -3., True),
                          (1., 1.1, 2., 2., 6., -3., False),
                          (1., 1., 2., 2.1, 6., -3., False),
                          (1., 1., 2., 2., 7., -3., False),
                          (1., 1., 2., 2., 6., -2., False), ])
def test_is_symmetrical(ta_u,
                        ta_l,
                        tb_u,
                        tb_l,
                        alpha_b,
                        alpha_c,
                        is_symmetrical_value):
    r"""Test the is_symmetrical() function of the NURBS foil generator

    Parameters
    ----------
    ta_u
    ta_l
    tb_u
    tb_l
    alpha_b
    alpha_c
    is_symmetrical_value : bool
        The expected value from is_symmetrical()

    """
    k = {'ta_u': ta_u,
         'ta_l': ta_l,
         'tb_u': tb_u,
         'tb_l': tb_l,
         'alpha_b': alpha_b,
         'alpha_c': alpha_c}
    assert NURBS(k).is_symmetrical() is is_symmetrical_value


@pytest.mark.parametrize("ta_u, ta_l, tb_u, tb_l, alpha_b, alpha_c,"
                         "is_valid_value",
                         [(1., 1., 2., 2., 6., -3., True),
                          (-1., 1., 2., 2., 6., -3., False),
                          (1., -1., 2., 2., 6., -3., False),
                          (1., 1., -2., 2., 6., -3., False),
                          (1., 1., 2., -2., 6., -3., False),
                          (1., 1., 2., 2., -6., -3., False), ])
def test_is_valid(ta_u, ta_l, tb_u, tb_l, alpha_b, alpha_c, is_valid_value):
    r"""Test the is_valid() function of the NURBS foil generator

    Parameters
    ----------
    ...
    is_valid_value : bool
        The expected value from is_valid()

    """
    k = {'ta_u': ta_u,
         'ta_l': ta_l,
         'tb_u': tb_u,
         'tb_l': tb_l,
         'alpha_b': alpha_b,
         'alpha_c': alpha_c}
    section = NURBS(k)
    assert section.is_valid() is is_valid_value


@pytest.mark.parametrize("ta_u, ta_l, tb_u, tb_l, alpha_b, alpha_c,"
                         "expected_value",
                         [(1., 1., 2., 2., 6., -3., 0.31241148952826625), ])
def test_max_thickness(ta_u,
                       ta_l,
                       tb_u,
                       tb_l,
                       alpha_b,
                       alpha_c,
                       expected_value,
                       tolerance=1e-4):
    r"""Test the max_thickness() function of the NURBS foil generator

    Parameters
    ----------
    ...
    expected_value : float
        The expected value from max_thickness()

    tolerance : float (optional, default is 1e-4)
        The tolerance for the value calculation

    """
    k = {'ta_u': ta_u,
         'ta_l': ta_l,
         'tb_u': tb_u,
         'tb_l': tb_l,
         'alpha_b': alpha_b,
         'alpha_c': alpha_c}
    section = NURBS(k)
    assert expected_value - tolerance <= section.max_thickness() <= expected_value + tolerance


@pytest.mark.parametrize("ta_u, ta_l, tb_u, tb_l, alpha_b, alpha_c",
                         [('unconvertable_to_float', 1., 2., 2., 6., -3.),
                          (1., 'unconvertable_to_float', 2., 2., 6., -3.),
                          (1., 1., 'unconvertable_to_float', 2., 6., -3.),
                          (1., 1., 2., 'unconvertable_to_float', 6., -3.),
                          (1., 1., 2., 2., 'unconvertable_to_float', -3.)])
def test_wrong_constructor_values(ta_u, ta_l, tb_u, tb_l, alpha_b, alpha_c):
    r"""Test instantiation with wrong parameters"""
    k = {'ta_u': ta_u,
         'ta_l': ta_l,
         'tb_u': tb_u,
         'tb_l': tb_l,
         'alpha_b': alpha_b,
         'alpha_c': alpha_c}
    with pytest.raises(ValueError):
        NURBS(k)


@pytest.mark.parametrize("ta_u, ta_l, tb_u, tb_l, alpha_b, alpha_c",
                         [(1., 1., 2., 2., 6., -3.), ])
def test_area(ta_u, ta_l, tb_u, tb_l, alpha_b, alpha_c):
    r"""Test the area() function of the NURBS generator"""
    k = {'ta_u': ta_u,
         'ta_l': ta_l,
         'tb_u': tb_u,
         'tb_l': tb_l,
         'alpha_b': alpha_b,
         'alpha_c': alpha_c}
    assert NURBS(k).area() > 0.0
