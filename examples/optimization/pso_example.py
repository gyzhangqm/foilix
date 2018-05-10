#!/usr/bin/env python
# coding: utf-8

r"""pso foil optimization example"""

import logging
# import time

import numpy as np
import wx

from foilix.optimization.pso import PsoAlgorithm
from foilix.optimization.scoring import CompoundScoreSectionScorer, \
    YachtAppendageParsecSectionScorer
# from foilix.ui.observer import Observer
from foilix.ui.logging_frame import LoggingFrame, NewLoggingFrame


# class Client(Observer):
#     r"""Very simple client that prints messages to stdout"""
#     def update(self, message, n, i_par, pts, score):
#         print("update client called")
#         print("%s - %i - %i - %s - %f" % (message,
#                                           n, i_par, str(pts), 1./score))


def compound_scoring_example():
    r"""Example use of CompoundScoreSectionScorer"""

    constraints = np.array(((0.01, 0.5),  # leading edge radius min and max
                            (.05, .9),  # x at max thickness min and max
                            (-1.0, 1.0),  # curvature min and max
                            (0.01, 20.0)))  # trailing edge angle min and max

    so = CompoundScoreSectionScorer(thickness=0.05,
                                    angles_of_attack=[0.0, 10.0, 1.0],
                                    reynolds=[5e4, 1e5],
                                    ncrits=[2.1],
                                    iterlim=100,
                                    max_lift_weight=0.01)
    algo = PsoAlgorithm(constraints, so)
    # client = Client()
    app = wx.App()
    dlg = LoggingFrame()
    dlg.Show()

    # algo.add_observers(client)
    algo.add_observers(dlg)

    algo.start()

    app.MainLoop()


def yacht_appendage_scoring_example():
    r"""Example use of CompoundScoreSectionScorer"""
    # constraints to be close to ht13, one of the best sections
    # for the operational conditions
    # 0.065 0.008 0.19 0.42 4.0 -> score: 32.4
    # global_best - 10 - 6 -
    #  [ 0.064       0.0060604   0.20602475 -0.51808584  4.19304666] - 33.171001
    constraints = np.array(((0.064, 0.007),  # thickness
                            (0.004, 0.012),   # leading edge radius min and max
                            (.13, .3),     # x at max thickness min and max
                            (-1.0, 1.0),   # curvature min and max
                            (3.0, 7.0)))  # trailing edge angle min and max

    # constraints to be close to s9033,
    # the best sections for the operational conditions
    # 0.075 0.0078 0.222 0.45 3.7 -> 32.435
    # global_best - 0 - 4 -
    #  [ 0.073       0.00417465  0.22934528 -0.70232411  3.6166232 ] - 32.644322
    # global_best - 0 - 9 -
    #  [ 0.073       0.00640035  0.22515226 -0.54439467  3.61586008] - 33.309707
    # global_best - 12 - 2 -
    #  [ 0.073       0.00553158  0.24408096 -0.48397659  4.33380002] - 33.343350
    constraints = np.array(((0.073, 0.0077),  # thickness
                            (0.004, 0.012),   # leading edge radius min and max
                            (.12, .32),     # x at max thickness min and max
                            (-1.0, 1.0),   # curvature min and max
                            (3.0, 5.0)))  # trailing edge angle min and max

    so = YachtAppendageParsecSectionScorer(angles_of_attack=[0.0, 6.0, 1.0],
                                           aoa_ld=[3., 4., 5.],
                                           reynolds=[1.5e4, 3e4, 4.5e4, 6e4],
                                           ncrits=[2.5, 3.],
                                           iterlim=200,
                                           inv_min_drag_scaling=0.25)
    algo = PsoAlgorithm(constraints, so)
    # client = Client()
    app = wx.App()
    dlg = NewLoggingFrame()
    dlg.Show()

    # algo.add_observers(client)
    algo.add_observers(dlg)

    algo.start()

    app.MainLoop()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s :: %(levelname)6s :: %(module)20s '
                               ':: %(lineno)3d :: %(message)s')
    # compound_scoring_example()
    yacht_appendage_scoring_example()
