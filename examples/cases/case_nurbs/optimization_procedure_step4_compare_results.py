#!/usr/bin/env python
# coding: utf-8

r"""Visualize the optimization results"""
from __future__ import print_function, division

import logging
from os import environ
from os.path import join, basename, dirname, isfile

import matplotlib
import matplotlib.pyplot as plt

# import foilix.xfoil.xfoil
from foilix.xfoil.polar import Polar

from foilix.foil_generators.nurbs import NURBS

import optimization_procedure_step0_define_problem as op_def

# Set the matplotlib rc_context from file
MATPLOTLIBRC = join(dirname(__file__), 'matplotlibrc_defaults')
matplotlib.rc_context(fname=MATPLOTLIBRC)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s :: %(levelname)6s :: %(module)20s :: '
                           '%(lineno)3d :: %(message)s')
logger = logging.getLogger(__name__)


# read global_best.data to rebuild foil
assert isfile(op_def.save_global_best_file)

with open(op_def.save_global_best_file) as f:
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
print(foil)
foil.plot_foil("Global best foil")

with open(op_def.global_best_dat_file, "w") as f:
    f.write("GB\n")
    f.write(foil.get_coords_plain())
# print(foil.get_coords_plain())

# compare against best of db digging


WORKING_DIRECTORY = join(dirname(__file__),
                         '../../../foilix/xfoil')
XFOIL_EXE_TO_DAT_RELPATH = '../../foil_dat/%s'

# Set the working directory to where the xfoil executable resides
logger.info("Changing working directory to : %s" % WORKING_DIRECTORY)
os.chdir(WORKING_DIRECTORY)

# Analysis configuration
angles_of_attack = op_def.aoa_spec
# use the average
reynolds_number = sum(op_def.reynolds_number)/len(op_def.reynolds_number)
ncrit = sum(op_def.ncrits)/len(op_def.ncrits)  # use the average

# Foils to analyze

# get the names of the best foils in db
with open(op_def.db_digging_filename) as f:
    lines = f.readlines()
foils_to_analyze = [lines[i].split(",")[0] for i in range(8, 11)]


# put the global best file in foil_data
import shutil
shutil.copyfile(op_def.global_best_dat_file,
                join(environ["FOIL_DATA_FOLDER"],
                     basename(op_def.global_best_dat_file)))

foils_to_analyze.append(basename(op_def.global_best_dat_file))

foils_dat_files = [XFOIL_EXE_TO_DAT_RELPATH % f for f in foils_to_analyze]


f, axarr = plt.subplots(2, 2)
axarr[-1, -1].axis('off')  # hide bottom right subplot that is not used
axarr[0, 0].set_title("Cl, Cd = f(angle)")
axarr[0, 1].set_title("Cl = f(Cd)")
axarr[1, 0].set_title("L/D = f(angle)")

colors = ["red", "orange", "pink", "blue"]

for i, dat_file in enumerate(foils_dat_files):
    polar = Polar(dat_file,
                  angles_of_attack,
                  reynolds_number,
                  ncrit,
                  iterlim=100)
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
os.remove(join(environ["FOIL_DATA_FOLDER"],
               basename(op_def.global_best_dat_file)))
