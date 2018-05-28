#!/usr/bin/env python
# coding: utf-8

r"""PARSEC foil generator tests"""

from __future__ import division, print_function

import pytest

from foilix.foil_generators.parsec import PARSEC


@pytest.mark.parametrize("rle, x_pre, y_pre, d2ydx2_pre, th_pre, x_suc, y_suc,"
                         "d2ydx2_suc, th_suc, xte, yte, is_symmetrical_value",
                         [(.005, 0.25, -0.03, 0.25, 6., 0.25, 0.03,
                           -0.25, -6., 1., 0., True),
                          # yte not zero
                          (.005, 0.25, -0.03, 0.25, 6., 0.25, 0.03,
                           -0.25, -6., 1., 0.001, False),
                          # diff. thicknesses
                          (.005, 0.25, -0.02, 0.25, 6., 0.25, 0.03,
                           -0.25, -6., 1., 0.0, False),
                          ])
def test_is_symmetrical(rle,
                        x_pre,
                        y_pre,
                        d2ydx2_pre,
                        th_pre,
                        x_suc,
                        y_suc,
                        d2ydx2_suc,
                        th_suc,
                        xte,
                        yte,
                        is_symmetrical_value):
    r"""Test the is_symmetrical() function of the PARSEC foil generator

    Parameters
    ----------
    rle
    x_pre
    y_pre
    d2ydx2_pre
    th_pre
    x_suc
    y_suc
    d2ydx2_suc
    th_suc
    xte
    yte
    is_symmetrical_value : bool
        The expected value from is_symmetrical()

    """
    k = {'rle': rle,
         'x_pre': x_pre,
         'y_pre': y_pre,
         'd2ydx2_pre': d2ydx2_pre,
         'th_pre': th_pre,
         'x_suc': x_suc,
         'y_suc': y_suc,
         'd2ydx2_suc': d2ydx2_suc,
         'th_suc': th_suc,
         'xte': xte,
         'yte': yte}
    assert PARSEC(k).is_symmetrical() is is_symmetrical_value


@pytest.mark.parametrize("rle, x_pre, y_pre, d2ydx2_pre, th_pre, x_suc, y_suc,"
                         "d2ydx2_suc, th_suc, xte, yte, is_valid_value",
                         [(.005, 0.25, -0.03, 0.25, 6., 0.25, 0.03,
                           -0.25, -6., 1., 0., True),
                          # assy
                          (.005, 0.25, -0.03, 0.25, 6., 0.25, 0.03,
                           -0.25, -6., 1., 0.001, "Exception raised"),
                          # assy
                          (.005, 0.25, -0.02, 0.25, 6., 0.25, 0.03,
                           -0.25, -6., 1., 0., "Exception raised"),
                          (.005, 0.25, -0.03, 0.47, 6., 0.25, 0.03,
                           -0.47, -6., 1., 0., False)])
def test_is_valid(rle,
                  x_pre,
                  y_pre,
                  d2ydx2_pre,
                  th_pre,
                  x_suc,
                  y_suc,
                  d2ydx2_suc,
                  th_suc,
                  xte,
                  yte,
                  is_valid_value):
    r"""Test the is_valid() function of the PARSEC foil generator

    Parameters
    ----------
    rle
    x_pre
    y_pre
    d2ydx2_pre
    th_pre
    x_suc
    y_suc
    d2ydx2_suc
    th_suc
    xte
    yte
    is_valid_value : bool
        The expected value from is_valid()

    """
    k = {'rle': rle,
         'x_pre': x_pre,
         'y_pre': y_pre,
         'd2ydx2_pre': d2ydx2_pre,
         'th_pre': th_pre,
         'x_suc': x_suc,
         'y_suc': y_suc,
         'd2ydx2_suc': d2ydx2_suc,
         'th_suc': th_suc,
         'xte': xte,
         'yte': yte}
    section = PARSEC(k)
    if section.is_symmetrical() is False:
        with pytest.raises(NotImplementedError):
            section.is_valid()
    else:
        assert section.is_valid() is is_valid_value


@pytest.mark.parametrize("rle, x_pre, y_pre, d2ydx2_pre, th_pre, x_suc, y_suc,"
                         "d2ydx2_suc, th_suc, xte, yte, expected_value",
                         [(.005, 0.25, -0.03, 0.25, 6., 0.25, 0.03,
                           -0.25, -6., 1., 0., 0.06),
                          # assy
                          (.005, 0.25, -0.03, 0.25, 6., 0.25, 0.03,
                           -0.25, -6., 1., 0.001, 0.06),
                          # assy
                          (.005, 0.25, -0.02, 0.25, 6., 0.25, 0.03,
                           -0.25, -6., 1., 0., 0.05),
                          (.005, 0.25, -0.03, 0.47, 6., 0.25, 0.03,
                           -0.47, -6., 1., 0., 0.06)])
def test_max_thickness(rle,
                       x_pre,
                       y_pre,
                       d2ydx2_pre,
                       th_pre,
                       x_suc,
                       y_suc,
                       d2ydx2_suc,
                       th_suc,
                       xte,
                       yte,
                       expected_value,
                       tolerance=1e-4):
    r"""Test the max_thickness() function of the PARSEC foil generator

    Parameters
    ----------
    rle
    x_pre
    y_pre
    d2ydx2_pre
    th_pre
    x_suc
    y_suc
    d2ydx2_suc
    th_suc
    xte
    yte
    expected_value : float
        The expected value from max_thickness()
    tolerance : float (optional, default is 1e-4)
        The tolerance for the value calculation

    """
    k = {'rle': rle,
         'x_pre': x_pre,
         'y_pre': y_pre,
         'd2ydx2_pre': d2ydx2_pre,
         'th_pre': th_pre,
         'x_suc': x_suc,
         'y_suc': y_suc,
         'd2ydx2_suc': d2ydx2_suc,
         'th_suc': th_suc,
         'xte': xte,
         'yte': yte}
    section = PARSEC(k)
    assert expected_value - tolerance <= section.max_thickness() <= expected_value + tolerance


@pytest.mark.parametrize("rle, x_pre, y_pre, d2ydx2_pre, th_pre, x_suc, y_suc,"
                         "d2ydx2_suc, th_suc, xte, yte",
                         # xte is not 1
                         [(.005, 0.25, -0.03, 0.25, 6., 0.25, 0.03,
                           -0.25, -6., .99, 0.), ])
def test_wrong_constructor_values(rle,
                                  x_pre,
                                  y_pre,
                                  d2ydx2_pre,
                                  th_pre,
                                  x_suc,
                                  y_suc,
                                  d2ydx2_suc,
                                  th_suc,
                                  xte,
                                  yte):
    r"""Test instantiation with wrong parameters"""
    k = {'rle': rle,
         'x_pre': x_pre,
         'y_pre': y_pre,
         'd2ydx2_pre': d2ydx2_pre,
         'th_pre': th_pre,
         'x_suc': x_suc,
         'y_suc': y_suc,
         'd2ydx2_suc': d2ydx2_suc,
         'th_suc': th_suc,
         'xte': xte,
         'yte': yte}
    with pytest.raises(ValueError):
        PARSEC(k)


@pytest.mark.parametrize("rle, x_pre, y_pre, d2ydx2_pre, th_pre, x_suc, y_suc,"
                         "d2ydx2_suc, th_suc, xte, yte",
                         [(.005, 0.25, -0.03, 0.25, 6., 0.25, 0.03,
                           -0.25, -6., 1., 0.),
                          # assy
                          (.005, 0.25, -0.03, 0.25, 6., 0.25, 0.03,
                           -0.25, -6., 1., 0.001),
                          # assy
                          (.005, 0.25, -0.02, 0.25, 6., 0.25, 0.03,
                           -0.25, -6., 1., 0.),
                          (.005, 0.25, -0.03, 0.47, 6., 0.25, 0.03,
                           -0.47, -6., 1., 0.)])
def test_area(rle,
              x_pre,
              y_pre,
              d2ydx2_pre,
              th_pre,
              x_suc,
              y_suc,
              d2ydx2_suc,
              th_suc,
              xte,
              yte):
    r"""Test the area() function of the PARSEC generator"""
    k = {'rle': rle,
         'x_pre': x_pre,
         'y_pre': y_pre,
         'd2ydx2_pre': d2ydx2_pre,
         'th_pre': th_pre,
         'x_suc': x_suc,
         'y_suc': y_suc,
         'd2ydx2_suc': d2ydx2_suc,
         'th_suc': th_suc,
         'xte': xte,
         'yte': yte}
    assert PARSEC(k).area() > 0.0


def test_symmetrical_parsec():
    r"""Test that comes from an old doctest"""
    # Symmetrical foil section
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
    assert foil.is_symmetrical() is True
    assert foil.is_valid() is True
