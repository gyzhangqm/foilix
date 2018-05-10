#!/usr/bin/env python
# coding: utf-8

r"""Step 3 of the optimization procedure

Launch a PSO optimization using initial foil data +- constraints as a starting point

"""

import logging
import time

import numpy as np
import wx

from foilix.optimization.pso import PsoAlgorithm
from foilix.optimization.scoring import YachtAppendageParsecSectionScorer
# from foilix.ui.observer import Observer
from foilix.ui.logging_frame import NewLoggingFrame
import optimization_procedure_step0_define_problem as op_def


def optimize_with_pso():
    r"""Example use of CompoundScoreSectionScorer"""

    # Read initial_parsec_foil_params.data to retrieve the initial values
    with open(op_def.initial_parsec_foil_params_filename) as f:
        lines = f.readlines()

    initial_thickness = float(lines[0].split(",")[1])
    initial_max_thickness_x = float(lines[1].split(",")[1])
    initial_curvature = float(lines[2].split(",")[1])
    initial_le_radius = float(lines[3].split(",")[1])
    initial_te_angle = float(lines[4].split(",")[1])

    constraints = np.array((
        # thickness
        (max(initial_thickness - op_def.thickness_plus_minus, 0.01),
         initial_thickness + op_def.thickness_plus_minus),
        # leading edge radius min and max
        (max(initial_le_radius - op_def.le_radius_plus_minus, 0.00001),
         initial_le_radius + op_def.le_radius_plus_minus),
        # x at max thickness min and max
        (max(initial_max_thickness_x - op_def.max_thickness_x_plus_minus, 1e-6),
         min(initial_max_thickness_x + op_def.max_thickness_x_plus_minus, 1.0)),
        # curvature min and max
        (initial_curvature - op_def.curvature_plus_minus,
         initial_curvature + op_def.curvature_plus_minus),
        # trailing edge angle min and max
        (max(initial_te_angle - op_def.te_angle_plus_minus, 0.),
         initial_te_angle + op_def.te_angle_plus_minus)))

    so = YachtAppendageParsecSectionScorer(angles_of_attack=op_def.aoa_spec,
                                           aoa_ld=op_def.aoa_ld,
                                           reynolds=op_def.reynolds_number,
                                           ncrits=op_def.ncrits,
                                           iterlim=200,
                                           inv_min_drag_scaling=op_def.inv_min_drag_scaling)

    algo = PsoAlgorithm(constraints,
                        so,
                        iterations=op_def.nb_iterations,
                        S=op_def.swarm_size,
                        omega=op_def.omega,
                        phi_p=op_def.phi_p,
                        phi_g=op_def.phi_g,
                        save_global_best=op_def.save_global_best_file)
    # algo = PsoAlgorithm(constraints,
    #                     so,
    #                     save_global_best=op_def.save_global_best_file)

    app = wx.App()
    dlg = NewLoggingFrame()
    dlg.Show()

    algo.add_observers(dlg)

    algo.start()

    app.MainLoop()

if __name__ == "__main__":
    from os import mkdir
    from os.path import join, dirname, isdir
    if not isdir(join(dirname(__file__), "logs")):
        mkdir(join(dirname(__file__), "logs"))
    logging.basicConfig(level=logging.INFO,
                        filename='logs/optimizer_%s.log' %
                                 time.strftime("%d%b%Y-%H%M%S",
                                               time.localtime()),
                        format='%(asctime)s :: %(levelname)6s :: %(module)20s '
                               ':: %(lineno)3d :: %(message)s')

    optimize_with_pso()
