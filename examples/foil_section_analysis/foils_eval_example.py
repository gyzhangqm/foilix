#!/usr/bin/env python
# coding: utf-8

r"""Foils evaluation example"""

import logging

from corelib.core.files import p_

from foilix.foils_eval import eval_foils
from foilix.filters import sort_foils_folder


def foils_eval_example():
    r"""Runs the example"""

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s :: %(levelname)6s :: %(module)20s '
                               ':: %(lineno)3d :: %(message)s')

    # f_s, f_u = sort_foils_folder(os.path.join(os.path.dirname(__file__),
    #                                                          "../foil_dat/"))
    f_s, _ = sort_foils_folder(p_(__file__, "../../foil_dat"))
    print("There are %i symmetrical foils in the foil_dat folder" % len(f_s))

    # add the almost symmetrical Drela foils (ht22 and ht23
    # are not symmetrical at all)
    f_s.append(p_(__file__, '../../foil_dat/ht05.dat'))
    f_s.append(p_(__file__, '../../foil_dat/ht08.dat'))
    f_s.append(p_(__file__, '../../foil_dat/ht12.dat'))
    f_s.append(p_(__file__, '../../foil_dat/ht13.dat'))
    f_s.append(p_(__file__, '../../foil_dat/ht14.dat'))

    # Angles, reynolds and ncrits must be in the database
    # (no interpolation at the moment)
    aoa_spec = (0., 10., 1.)
    rns = [1.5e4, 3e4, 4.5e4, 6e4]
    # ncs = [1.5, 2.]
    ncs = [2.5, 3.]
    aoa_ld = [3., 4., 5.]
    inv_min_drag_scaling = 0.25

    eval_foils(
        foil_data_folder="../../foil_data",
        file_list=f_s,
        logfile_name="eval_foil_as%s_rn%s_"
                     "nc%s_ald%s_imds%s.csv" % (str(aoa_spec),
                                                str(rns),
                                                str(ncs),
                                                str(aoa_ld),
                                                str(inv_min_drag_scaling)
                                                ),
        max_thickness=0.5,
        angles_of_attack_spec=aoa_spec,
        reynolds_numbers=rns,
        ncrits=ncs,
        aoa_ld=aoa_ld,
        inv_min_drag_scaling=inv_min_drag_scaling,
        log=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s :: %(levelname)6s :: %(module)20s '
                               ':: %(lineno)3d :: %(message)s')
    foils_eval_example()
