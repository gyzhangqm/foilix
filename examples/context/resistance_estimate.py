#!/usr/bin/env python
# coding: utf-8

r"""Resistance estimates for a RG65. Orders of magnitude.

Not directly related to 2d sections optimization,
only to estimate the importance of foil drag contribution to total drag

"""

from __future__ import print_function

import logging
from math import sqrt

from hydro.appendage.viscous import appendage_viscous
from hydro.hull.viscous import hull_viscous
from hydro.hull.residuary_la import HullResiduaryResistanceLa
from hydro.hull.residuary_ks import HullResiduaryResistanceKs


def resistance_estimate():
    r"""Runs the example"""
    lwl = 0.65
    v = 1.2  # m/s
    cd = 0.013  # typical drag coefficient of a 2d foil section around rn = 60k
    foil_area = (0.06 * 0.3)

    # Foil resistance estimate using Cd
    r_foil_from_cd = 0.5 * 1000 * foil_area * v ** 2 * cd

    # resistance using fshydro
    r_foil_appendage_viscous = -appendage_viscous(v,
                                                  0.,
                                                  [0, 0, 0],
                                                  0.055,
                                                  0.1,
                                                  2 * foil_area).x

    sh = (646 / 10000.)  # hull wetted area
    resistance_hull_viscous = hull_viscous(boatspeed=v, lwl=lwl, Sc=sh)

    hrr_la = HullResiduaryResistanceLa(Vc=1080. / 100**3,
                                       lwl=lwl,
                                       bwl=0.1,
                                       Tc=0.04,
                                       Aw=485. / 100**2)
    hrr_ks = HullResiduaryResistanceKs(Vc=1080. / 100**3,
                                       lwl=lwl,
                                       bwl=0.1,
                                       Aw=485. / 100**2,
                                       Sc=sh)

    # voiles
    tws = 3
    force_in_sails_downwind = 0.5 * 1.3 * 0.5 * (tws - v) ** 2 * 0.9

    # Froude number
    print("Boatspeed : %f m/s" % v)
    print("Fn : %f" % (v/sqrt(9.81*lwl)))  # Froude number

    # Foil
    print("Foil area: %f m2" % foil_area)
    print("R foil (using Cd): %f N" % r_foil_from_cd)
    print("R foil (using appendage viscous): %f N" % r_foil_appendage_viscous)

    # hull
    print("Hull WSA : %f m2" % sh)
    print("Hull R viscous : %f N" % -resistance_hull_viscous.x)

    print("Hull R residuary (Larson) : %f N" % -hrr_la.force(v).x)
    print("Hull R residuary (Keuning) : %f N" % -hrr_ks.force(v).x)

    # r tot
    print("R total : %f N" %
          (r_foil_from_cd - resistance_hull_viscous.x - hrr_la.force(v).x))

    print("Force in sails (downwind at speed %f m/s) : %f N" %
          (v, force_in_sails_downwind))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s :: %(levelname)6s :: %(module)20s '
                               ':: %(lineno)3d :: %(message)s')
    resistance_estimate()
