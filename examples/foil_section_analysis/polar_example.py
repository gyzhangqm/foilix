#!/usr/bin/python
# coding: utf-8

r"""Polar example
"""

from __future__ import print_function

from foilix.xfoil.polar import Polar

reynolds_number = [2.5e4, 3.5e4, 3.5e4, 4.5e4]
ncrits = [2.5, 3.]

polar = Polar("../../foil_dat/gf_0001.dat", [0, 7, 1], 2.5e4, 3.)
polar.compute()

print("--interp_aoas--")
print(polar.interp_aoas)
print("--warnings--")
print(polar.warnings)
print("--angles_of_attack_computed--")
print(polar.angles_of_attack_computed)
print("--coefficients_of_lift--")
print(polar.coefficients_of_lift)
print("--coefficients_of_drag--")
print(polar.coefficients_of_drag)
print("--lift_to_drag--")
print(polar.lift_to_drag)
print("--maximum_lift--")
print(polar.maximum_lift)
print("--minimum_drag--")
print(polar.minimum_drag)
print("--max_lift_to_drag--")
print(polar.max_lift_to_drag)
