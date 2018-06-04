#!/usr/bin/env python
# coding: utf-8

r"""Step 3 of the optimization procedure

Launch a PSO optimization using initial foil data +- constraints
as a starting point

"""

from os import getcwd, mkdir
from os.path import join, isdir
import logging
import time
from argparse import ArgumentParser

import numpy as np
import wx

from foilix.optimization.pso import PsoAlgorithm
from foilix.optimization.scoring import YachtAppendageNurbsSectionScorer, \
    YachtAppendageParsecSectionScorer
from foilix.ui.logging_frame import NewLoggingFrame
from foilix.read_config import read_config

config = read_config(join(getcwd(), "foilix_case.conf"))


def optimize_with_pso_nurbs():
    r"""Example use of CompoundScoreSectionScorer"""

    # Read initial_parsec_foil_params.data to retrieve the initial values
    with open(join(getcwd(), "initial_nurbs_foil_params.data")) as f:
        lines = f.readlines()

    initial_ta = float(lines[0].split(",")[1])
    initial_tb = float(lines[1].split(",")[1])
    initial_alpha = float(lines[2].split(",")[1])

    constraints = np.array(((max(initial_ta - config["ta_plus_minus"], 1e-6),
                             initial_ta + config["ta_plus_minus"]),  # ta

                            (max(initial_tb - config["tb_plus_minus"], 1e-6),
                             initial_tb + config["tb_plus_minus"]),   # tb

                            # alpha
                            (max(initial_alpha - config["alpha_plus_minus"], 1e-6),
                             min(initial_alpha + config["alpha_plus_minus"], 1.0))
                            ))
    so = YachtAppendageNurbsSectionScorer(angles_of_attack=config["aoa_spec"],
                                          aoa_ld=config["aoa_ld"],
                                          reynolds=config["reynolds_numbers"],
                                          ncrits=config["ncrits"],
                                          iterlim=200,
                                          inv_min_drag_scaling=config["inv_min_drag_scaling"])

    return constraints, so


def optimize_with_pso_parsec():
    r"""Example use of CompoundScoreSectionScorer"""

    # Read initial_parsec_foil_params.data to retrieve the initial values
    with open(join(getcwd(), "initial_parsec_foil_params.data")) as f:
        lines = f.readlines()

    initial_thickness = float(lines[0].split(",")[1])
    initial_max_thickness_x = float(lines[1].split(",")[1])
    initial_curvature = float(lines[2].split(",")[1])
    initial_le_radius = float(lines[3].split(",")[1])
    initial_te_angle = float(lines[4].split(",")[1])

    constraints = np.array((
        # thickness
        (max(initial_thickness - config["thickness_plus_minus"], 0.01),
         initial_thickness + config["thickness_plus_minus"]),
        # leading edge radius min and max
        (max(initial_le_radius - config["le_radius_plus_minus"], 0.00001),
         initial_le_radius + config["le_radius_plus_minus"]),
        # x at max thickness min and max
        (max(initial_max_thickness_x - config["max_thickness_x_plus_minus"], 1e-6),
         min(initial_max_thickness_x + config["max_thickness_x_plus_minus"], 1.0)),
        # curvature min and max
        (initial_curvature - config["curvature_plus_minus"],
         initial_curvature + config["curvature_plus_minus"]),
        # trailing edge angle min and max
        (max(initial_te_angle - config["te_angle_plus_minus"], 0.),
         initial_te_angle + config["te_angle_plus_minus"])))

    so = YachtAppendageParsecSectionScorer(angles_of_attack=config["aoa_spec"],
                                           aoa_ld=config["aoa_ld"],
                                           reynolds=config["reynolds_numbers"],
                                           ncrits=config["ncrits"],
                                           iterlim=200,
                                           inv_min_drag_scaling=config["inv_min_drag_scaling"])

    return constraints, so


def main(parameterization):

    if parameterization == "nurbs":
        constraints, so = optimize_with_pso_nurbs()
    elif parameterization == "parsec":
        constraints, so = optimize_with_pso_parsec()
    else:
        raise ValueError("Parameterization must be nurbs or parsec")

    algo = PsoAlgorithm(constraints,
                        so,
                        iterations=12,
                        S=12,
                        omega=-0.2,  # Particle velocity scaling factor
                        phi_p=0.0,  # Scaling factor to search away from the particle’s best known position
                        phi_g=2.8,  # Scaling factor to search away from the swarm’s best known position
                        save_global_best=join(getcwd(), "global_best.data"))

    app = wx.App()
    dlg = NewLoggingFrame()
    dlg.Show()
    algo.add_observers(dlg)
    algo.start()
    app.MainLoop()


if __name__ == "__main__":

    if not isdir(join(getcwd(), "logs")):
        mkdir(join(getcwd(), "logs"))

    logging.basicConfig(level=logging.INFO,
                        filename='logs/optimizer_%s.log' %
                                 time.strftime("%d%b%Y-%H%M%S",
                                               time.localtime()),
                        format='%(asctime)s :: %(levelname)6s :: %(module)20s '
                               ':: %(lineno)3d :: %(message)s')

    parser = ArgumentParser(description="Foilix Opt step 3")
    parser.add_argument('-n', '--nurbs',
                        action='store_true',
                        help="Use NURBS parameterization")
    parser.add_argument('-p', '--parsec',
                        action='store_true',
                        help="Use PARSEC parameterization")
    args = parser.parse_args()
    if args.nurbs is True:
        if args.parsec is True:
            raise ValueError("Specify a single parameterization to use")
        else:
            main("nurbs")
    else:
        if args.parsec is True:
            main("parsec")
        else:
            raise ValueError("Specify which parameterization to use")
