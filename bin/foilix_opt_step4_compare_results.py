#!/usr/bin/env python
# coding: utf-8

r"""Visualize the optimization results"""
from __future__ import print_function, division

from os import getcwd, chdir
from os.path import join, basename, dirname, isfile
from argparse import ArgumentParser
import shutil

import matplotlib
import matplotlib.pyplot as plt

from foilix.xfoil.polar import Polar

from foilix.foil_generators.nurbs import NURBS
from foilix.foil_generators.parsec import PARSEC
from foilix.read_config import read_config

config = read_config(join(getcwd(), "foilix_case.conf"))


def nurbs_foil():
    with open(join(getcwd(), "global_best_nurbs.data")) as f:
        lines = f.readlines()

    ta = float(lines[3])
    tb = float(lines[4])
    alpha = float(lines[5])

    k = {'ta_u': ta,
         'ta_l': ta,
         'tb_u': tb,
         'tb_l': tb,
         'alpha_b': 2*alpha,
         'alpha_c': -alpha}

    foil = NURBS(k)
    return foil


def parsec_foil():
    with open(join(getcwd(), "global_best_parsec.data")) as f:
        lines = f.readlines()

    thickness = float(lines[3])
    le_radius = float(lines[4])
    max_thickness_x = float(lines[5])
    curvature = float(lines[6])
    te_angle = float(lines[7])

    k = {'rle': le_radius,
         'x_pre': max_thickness_x,
         'y_pre': -thickness / 2.,
         'd2ydx2_pre': -curvature,
         'th_pre': te_angle,
         'x_suc': max_thickness_x,
         'y_suc': thickness / 2.,
         'd2ydx2_suc': curvature,
         'th_suc': -te_angle,
         'xte': 1.,
         'yte': 0.}

    foil = PARSEC(k)
    return foil


def main(parameterization):
    # Set the matplotlib rc_context from file
    MATPLOTLIBRC = join(dirname(__file__), 'matplotlibrc_defaults')
    matplotlib.rc_context(fname=MATPLOTLIBRC)

    # read global_best.data to rebuild foil
    if parameterization == "nurbs":
        global_best_data_file = "global_best_nurbs.data"
        global_best_dat_file = "global_best_nurbs.dat"
        if not isfile(join(getcwd(), global_best_data_file)):
            msg = "Cannot find global_best_nurbs.data in CWD"
            # logger.critical(msg)
            raise AssertionError(msg)
        foil = nurbs_foil()
    elif parameterization == "parsec":
        global_best_data_file = "global_best_parsec.data"
        global_best_dat_file = "global_best_parsec.dat"
        if not isfile(join(getcwd(), global_best_data_file)):
            msg = "Cannot find global_best_parsec.data in CWD"
            # logger.critical(msg)
            raise AssertionError(msg)
        foil = parsec_foil()
    else:
        raise ValueError("Parameterization should be nurbs or parsec")

    print(foil)

    foil.plot_foil("Global best %s foil" % parameterization)

    with open(join(getcwd(), global_best_dat_file), "w") as f:
        f.write("GB\n")
        f.write(foil.get_coords_plain())
    # print(foil.get_coords_plain())

    # compare against best of db digging

    WORKING_DIRECTORY = join(dirname(__file__),
                             '../../foilix/xfoil')
    XFOIL_EXE_TO_DAT_RELPATH = '../foil_dat/%s'

    INITIAL_WORKDIR = getcwd()

    # Set the working directory to where the xfoil executable resides
    print("Changing working directory to : %s" % WORKING_DIRECTORY)
    chdir(WORKING_DIRECTORY)

    # Analysis configuration
    angles_of_attack = config["aoa_spec"]
    # use the average
    reynolds_number = sum(config["reynolds_numbers"]) / len(config["reynolds_numbers"])
    ncrit = sum(config["ncrits"]) / len(config["ncrits"])  # use the average

    # Foils to analyze

    # get the names of the best foils in db
    with open(join(INITIAL_WORKDIR, "data_digging.csv")) as f:
        lines = f.readlines()
    foils_to_analyze = [lines[i].split(",")[0] for i in range(8, 11)]

    # put the global best file in foil_data
    global_best_dat = join(INITIAL_WORKDIR, global_best_dat_file)
    shutil.copyfile(global_best_dat,
                    join(config["foil_dat_folder"],
                         basename(global_best_dat)))

    foils_to_analyze.append(basename(global_best_dat))

    foils_dat_files = [XFOIL_EXE_TO_DAT_RELPATH % f for f in foils_to_analyze]

    f, axarr = plt.subplots(2, 2)
    axarr[-1, -1].axis('off')  # hide bottom right subplot that is not used
    axarr[0, 0].set_title("Cl, Cd = f(angle)")
    axarr[0, 1].set_title("Cl = f(Cd)")
    axarr[1, 0].set_title("L/D = f(angle)")

    colors = ["red", "orange", "pink", "blue"]

    for i, dat_file in enumerate(foils_dat_files):
        print("**** analyzing : %s ****" % dat_file)
        try:
            polar = Polar(config["foil_data_folder"],
                          dat_file,
                          angles_of_attack,
                          reynolds_number,
                          ncrit,
                          iterlim=100,
                          use_precomputed_data=True)
            polar.compute()
        except FileNotFoundError:
            print("CWD : %s" % getcwd())
            print("dat_file : %s" % dat_file)
            polar = Polar("",
                          dat_file,
                          angles_of_attack,
                          reynolds_number,
                          ncrit,
                          iterlim=100,
                          use_precomputed_data=False)
            polar.compute()

        print("Max L/D : %f @ %f°" % (polar.max_lift_to_drag[0],
                                      polar.max_lift_to_drag[1]))
        print("%i angles computed out of %i specified" %
              (len(polar.angles_of_attack_computed),
               len(polar.angles_of_attack_spec)))

        # Plot Cl, Cd = f(angle)
        axarr[0, 0].plot(polar.interp_aoas,
                         [polar.coefficients_of_lift_interpolator(aoa)
                          for aoa in polar.interp_aoas],
                         'r-',
                         label="%s" % basename(dat_file),
                         color=colors[i])
        axarr[0, 0].scatter(polar.angles_of_attack_computed,
                            polar.coefficients_of_lift,
                            color=colors[i])
        axarr[0, 0].plot(polar.interp_aoas,
                         [polar.coefficients_of_drag_interpolator(aoa)
                          for aoa in polar.interp_aoas],
                         'r--',
                         color=colors[i])
        axarr[0, 0].scatter(polar.angles_of_attack_computed,
                            polar.coefficients_of_drag,
                            color=colors[i])
        leg = axarr[0, 0].legend(loc="upper left")
        if leg:
            leg.draggable()

        # Plot Cl = f(Cd)
        axarr[0, 1].plot([polar.coefficients_of_drag_interpolator(aoa)
                          for aoa in polar.interp_aoas],
                         [polar.coefficients_of_lift_interpolator(aoa)
                          for aoa in polar.interp_aoas],
                         'r-',
                         label="%s Cl" % basename(dat_file),
                         color=colors[i])
        axarr[0, 1].scatter(polar.coefficients_of_drag,
                            polar.coefficients_of_lift,
                            color=colors[i])

        # Plot L/D = f(aoa)
        axarr[1, 0].plot(polar.interp_aoas,
                         [polar.lift_to_drag_interpolator(aoa)
                          for aoa in polar.interp_aoas],
                         'r-',
                         label="%s L/D" % basename(dat_file),
                         color=colors[i])
        axarr[1, 0].scatter(polar.angles_of_attack_computed,
                            polar.lift_to_drag,
                            color=colors[i])

    plt.gcf().suptitle(str("%s reynolds; %s ncrit" % (str(reynolds_number),
                                                      str(ncrit))))
    plt.show()
    os.remove(join(config["foil_dat_folder"],
                   basename(global_best_dat)))

    print("Changing working directory back to : %s" % INITIAL_WORKDIR)
    chdir(INITIAL_WORKDIR)


if __name__ == "__main__":
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


