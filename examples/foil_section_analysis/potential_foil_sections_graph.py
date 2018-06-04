#!/usr/bin/env python
# coding: utf-8

r"""Graph of L/D at a given AoA
    x : Reynolds
    y : L/D at 6° AoA
"""
from __future__ import print_function

import logging

from foilix.data_api import get_data_tuple
from matplotlib import pyplot as plt
import os.path


def potential_foil_sections_analysis(foil_ids, rns, ncrits, aoa):
    r"""Runs the example"

    Parameters
    ----------
    foil_ids
    rns
    ncrits
    aoa

    """

    figure = plt.figure()

    axes = figure.add_subplot(111)

    colors = ['red', 'blue', 'orange', 'black']

    for i, foil_id in enumerate(foil_ids):
        for nc in ncrits:
            l_to_d = list()
            rnsc = rns[:]
            for rn in rns:
                try:
                    cl, cd, _, _, _, _ = \
                        get_data_tuple("../../foil_data",
                                       foil_id,
                                       mach=0.,
                                       ncrit=nc,
                                       reynolds=rn,
                                       aoa=aoa)
                    l_to_d.append(cl/cd)
                except TypeError:
                    print("data not found")
                    rnsc.remove(rn)
            axes.plot(rnsc,
                      l_to_d,
                      color=colors[i],
                      label="%s - ncrit=%.1f" % (os.path.basename(foil_id),
                                                 nc))

    axes.set_title("L/D at %.1f deg" % aoa)

    legend = axes.legend(loc='upper left', shadow=True)
    if legend is not None:
        for label in legend.get_texts():
            label.set_fontsize('small')
        legend.draggable()
    plt.show()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s :: %(levelname)6s :: %(module)20s '
                               ':: %(lineno)3d :: %(message)s')
    potential_foil_sections_analysis(foil_ids=["hq07",
                                               "s1010",
                                               "naca0006",
                                               "n0009sm"],
                                     rns=[1.5e4, 3e4, 4.5e4, 6e4],
                                     ncrits=[1.5, 2.],
                                     aoa=6.)
