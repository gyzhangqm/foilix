#!/usr/bin/env python
# coding: utf-8

r"""Compare the same NACA4 from a dat file and from the generator"""

from __future__ import print_function

import os

from corelib.core.files import p_

from foilix.foil import Foil
from foilix.foil_generators.naca4 import NACA4

naca4_dat = Foil.from_dat_file(p_(__file__, "../../foil_dat/naca0006.dat"))
naca4_gen = NACA4(0, 0, thickness=6)

print(naca4_dat.y_spread)
print(naca4_gen.max_thickness())

print(naca4_dat.max_y_x)

print(naca4_dat.is_symmetrical())
print(naca4_gen.is_symmetrical())
