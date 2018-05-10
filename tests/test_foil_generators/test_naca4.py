#!/usr/bin/env python
# coding: utf-8

r"""Test NACA4 foil generator"""

from __future__ import division, print_function

import pytest

from foilix.foil_generators.naca4 import NACA4


@pytest.mark.parametrize(
    "max_camber, max_camber_position, thickness, is_symmetrical_value",
    [
     (10, 3, 10, False),
     (0, 3, 6, True),
     (0, 0, 6, True)])
def test_is_symmetrical(max_camber,
                        max_camber_position,
                        thickness,
                        is_symmetrical_value):
    r"""Test the is_symmetrical() function of the NACA4 foil generator

    Parameters
    ----------
    max_camber
    max_camber_position
    thickness
    is_symmetrical_value

    """
    section = NACA4(max_camber=max_camber,
                    max_camber_position=max_camber_position,
                    thickness=thickness)
    assert section.is_symmetrical() is is_symmetrical_value


@pytest.mark.parametrize("max_camber, max_camber_position, thickness",
                         [(-10, 3, 10),
                          (0, -3, 10),
                          (0, 0, -15)])
def test_invalid_constructor_parameters(max_camber,
                                        max_camber_position,
                                        thickness):
    r"""Test an instantiation of the NACA4 foil generator
    with invalid parameters

    Parameters
    ----------
    max_camber
    max_camber_position
    thickness

    """
    with pytest.raises(ValueError):
        # Symmetrical airfoil section, invalid (negative thickness)
        NACA4(max_camber=max_camber,
              max_camber_position=max_camber_position,
              thickness=thickness)


@pytest.mark.parametrize("thickness_percent, thickness", [(15, 0.15),
                                                          (10, 0.1),
                                                          (6.5, 0.065)])
def test_max_thickness(thickness_percent, thickness, tolerance=1e-6):
    r"""Test the is_symmetrical() function of the NACA4 foil generator

    Parameters
    ----------
    thickness_percent : float
        Thickness in percents of chord
    thickness : float
        Thickness between 0 and 1

    tolerance : float (optional, default is 1e-5)
        The tolerance for the max value calculation

    """
    symmetrical_section_ = NACA4(max_camber=0,
                                 max_camber_position=0,
                                 thickness=thickness_percent)
    # error = 1e-4
    assert thickness - tolerance <= symmetrical_section_.max_thickness() <= thickness + tolerance


@pytest.mark.parametrize("max_camber, max_camber_position, thickness",
                         [(10, 3, 10),
                          (0, 3, 6),
                          (0, 0, 6)])
def test_area(max_camber, max_camber_position, thickness):
    r"""Test the area() function of the NACA4 foil generator

    Parameters
    ----------
    max_camber
    max_camber_position
    thickness

    """
    section = NACA4(max_camber=max_camber,
                    max_camber_position=max_camber_position,
                    thickness=thickness)
    assert section.area() > 0.0
