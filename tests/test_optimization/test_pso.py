#!/usr/bin/env python
# coding: utf-8

r"""PSO tests"""

from copy import copy

import numpy as np

from foilix.optimization.pso import Particle


def test_pso():
    """Unit tests for this class."""
    # __init__
    c = ((1, 2), (4, 5), (0, 1))
    p = Particle(c)

    # randomize
    # Copy because Python makes a reference if you say var = obj
    a = copy(p.pts)
    p.randomize()

    # try:
    #     np.testing.assert_array_almost_equal(a, p.pts)
    #     raise Warning("Randomized Particle has same pts as before")
    # except AssertionError:
    #     pass

    # APSO
    # Make p.pts equal to globMin (first argument) with B=1 and a=0
    p.APSO((3, 2, 0), 1, 0)
    p.APSO((3, 1, 0), .5, 0)
    print(p.pts)
    np.testing.assert_array_almost_equal(p.pts, np.array([2.0, 4.0, 0.0]))
