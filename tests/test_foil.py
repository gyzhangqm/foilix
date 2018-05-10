#!/usr/bin/env python
# coding: utf-8

r"""foil.py module tests"""

import pytest

from foilix.foil import Foil
import os.path


@pytest.mark.parametrize("dat_file, is_symmetrical_expected", [
    ("../foil_dat/sc20402.dat", False),
    ("../foil_dat/sc20403.dat", False),
    ("../foil_dat/stcyr171.dat", False),
    ("../foil_dat/naca0006.dat", True),
    ("../foil_dat/gf_topiko.dat", True),
    ("../foil_dat/clarky.dat", False)])  # clarky is in Lednicer format
def test_foil_symmetry(dat_file, is_symmetrical_expected):
    r"""Test if the symmetry is correctly evaluated

    Parameters
    ----------
    dat_file : str
        Relative path to the dat file
    is_symmetrical_expected : bool
        The expected result of a call to is_symmetrical()

    """
    path = os.path.join(os.path.dirname(__file__), dat_file)
    sc = Foil.from_dat_file(path)
    assert sc.is_symmetrical() is is_symmetrical_expected


@pytest.mark.parametrize("dat_file, y_spread_expected", [
    ("../foil_dat/naca0006.dat", 0.06002),
    # clarky is in Lednicer format
    ("../foil_dat/clarky.dat", 0.0916266 - (-.0302546))])
def test_y_spread(dat_file, y_spread_expected):
    r"""Test thickness computed from definition points

    Parameters
    ----------
    dat_file : str
        Relative path to the dat file
    y_spread_expected : bool
        The expected result of a call to the y_spread property

    """
    path = os.path.join(os.path.dirname(__file__), dat_file)
    naca = Foil.from_dat_file(path)
    assert naca.y_spread == y_spread_expected


@pytest.mark.parametrize("dat_file,max_y_x_expected", [
    ("../foil_dat/naca0006.dat", 0.3),
    ("../foil_dat/clarky.dat", 0.36)])  # clarky is in Lednicer format
def test_max_y_x(dat_file, max_y_x_expected):
    r"""Test position of maximum thickness computed from definition points

    Parameters
    ----------
    dat_file : str
        Relative path to the dat file
    max_y_x_expected : bool
        The expected maximum y x position

    """
    path = os.path.join(os.path.dirname(__file__), dat_file)
    naca = Foil.from_dat_file(path)
    assert naca.max_y_x == max_y_x_expected


@pytest.mark.parametrize("dat_file,min_y_x_expected", [
    ("../foil_dat/naca0006.dat", 0.3),
    ("../foil_dat/clarky.dat", 0.16)])  # clarky is in Lednicer format
def test_min_y_x(dat_file, min_y_x_expected):
    r"""Test position of minimum thickness computed from definition points

    Parameters
    ----------
    dat_file : str
        Relative path to the dat file
    min_y_x_expected : bool
        The expected minimum y x position

    """
    path = os.path.join(os.path.dirname(__file__), dat_file)
    naca = Foil.from_dat_file(path)
    assert naca.min_y_x == min_y_x_expected


@pytest.mark.skip(reason="functionality in development")
def test_leading_edge_radius_naca_0010():
    r"""Test leading edge radius computed from definition points"""
    path = os.path.join(os.path.dirname(__file__), "../foil_dat/naca0010.dat")
    naca = Foil.from_dat_file(path)
    ler = naca.pseudo_leading_edge_radius
    ler_theory = 1.1019 * (naca.y_spread ** 2)
    assert ler_theory == ler


@pytest.mark.skip(reason="functionality in development")
def test_leading_edge_radius_naca_0006():
    r"""Test leading edge radius computed from definition points"""
    path = os.path.join(os.path.dirname(__file__), "../foil_dat/naca0006.dat")
    naca = Foil.from_dat_file(path)
    ler = naca.pseudo_leading_edge_radius
    ler_theory = 1.1019 * (naca.y_spread ** 2)
    assert ler_theory == ler
