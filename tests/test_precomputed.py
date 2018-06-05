#!/usr/bin/env python
# coding: utf-8

r"""test xfoil.py module"""

import os

from foilix.data_api import get_data_tuple
from foilix.xfoil.xfoil import oper_visc_alpha

XFOIL_EXE_TO_DAT_RELPATH = '../../foil_dat/%s.dat'

cwd = os.getcwd()
os.chdir(os.path.join(os.path.dirname(__file__), "../foilix/xfoil"))
xfoil_exe_dir = os.path.join(os.path.dirname(__file__), "../foilix/xfoil")


def test_precomputed():
    r"""Test pre-computed data vs live computed data"""
    os.chdir(xfoil_exe_dir)

    foil_id = "naca0006"
    nc = 2.
    rn = 20000
    aoa = 5
    cl_pre, cd_pre, cdp_pre, cm_pre, top_xtr_pre, bot_xtr_pre = \
        get_data_tuple(foil_data_folder="../../foil_data",
                       foil_id=foil_id,
                       mach=0.,
                       ncrit=nc,
                       reynolds=rn,
                       aoa=aoa)

    # compute for a single angle
    data = \
        oper_visc_alpha(XFOIL_EXE_TO_DAT_RELPATH % foil_id,
                        operating_point=[aoa, aoa, 0.],
                        reynolds=rn,
                        mach=0.,
                        normalize=True,
                        show_seconds=None,
                        iterlim=None,
                        gen_naca=False,
                        n_crit=nc)[0][0]

    # data[0] is the angle of attack, which we already know
    cl, cd, cdp, cm, top_xtr, bot_xtr = \
        data[1], data[2], data[3], data[4], data[5], data[6],

    tolerance_default = 1e-8

    assert abs(cl_pre - cl) < tolerance_default
    assert abs(cd_pre - cd) < tolerance_default
    assert abs(cdp_pre - cdp) < tolerance_default
    assert abs(top_xtr_pre - top_xtr) < tolerance_default
    assert abs(bot_xtr_pre - bot_xtr) < tolerance_default

    os.chdir(cwd)
