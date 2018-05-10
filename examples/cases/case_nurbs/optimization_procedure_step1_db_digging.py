#!/usr/bin/env python
# coding: utf-8

r"""Step 1 of the global process of optimizing a 2D foil section

Find the best 2D sections in DB for the defined problem.
The output of this step is a CSV file where the 2D sections are ranked
from best (score) to worst

"""

from os import environ
from os.path import join, dirname, isfile
import logging
import matplotlib
from matplotlib import pyplot as plt

from foilix.foils_eval import sort_foils_folder, eval_foils
import optimization_procedure_step0_define_problem as op_def

# Set the matplotlib rc_context from file
MATPLOTLIBRC = os.path.join(os.path.dirname(__file__), 'matplotlibrc_defaults')
matplotlib.rc_context(fname=MATPLOTLIBRC)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s :: %(levelname)6s :: %(module)20s :: '
                           '%(lineno)3d :: %(message)s')
logger = logging.getLogger(__name__)

# Retrieve the path to the foil data folder (folder that contains the dat files)
try:
    foil_data_folder = environ["FOIL_DATA_FOLDER"]
    logger.info("Foil data folder : %s" % foil_data_folder)
except KeyError:
    logger.critical("FOIL_DATA_FOLDER environment variable must be set")
    raise KeyError("FOIL_DATA_FOLDER is not set")

# check that the FOILIX_DB_SQLITE_PATH environment variable is set
try:
    foilix_db_sqlite_path = environ["FOILIX_DB_SQLITE_PATH"]
    logger.info("Foilix sqlite DB path : %s" % foilix_db_sqlite_path)
except KeyError:
    logger.critical("FOILIX_DB_SQLITE_PATH environment variable must be set")
    raise KeyError("FOILIX_DB_SQLITE_PATH is not set")

# The presence of the db digging results file blocks re-execution
if not isfile(join(dirname(__file__), op_def.db_digging_filename)):
    # ------------------------------------------------------------------
    # Evaluate foils in database with scoring / find the best candidates
    # ------------------------------------------------------------------
    symmetrical_sections_filepaths, assymetrical_sections_filepaths = \
        sort_foils_folder(foil_data_folder)
    logger.info("There are %i symmetrical foils in the foils database" %
                len(symmetrical_sections_filepaths))
    print(symmetrical_sections_filepaths)

    # add the almost symmetrical Drela foils
    # (ht22 and ht23 are not symmetrical at all)
    symmetrical_sections_filepaths.append(join(foil_data_folder, 'ht05.dat'))
    symmetrical_sections_filepaths.append(join(foil_data_folder, 'ht08.dat'))
    symmetrical_sections_filepaths.append(join(foil_data_folder, 'ht12.dat'))
    symmetrical_sections_filepaths.append(join(foil_data_folder, 'ht13.dat'))
    symmetrical_sections_filepaths.append(join(foil_data_folder, 'ht14.dat'))

    # eval_foil uses the yacht_appendage_scoring function
    eval_foils(file_list=symmetrical_sections_filepaths,
               logfile_name=op_def.db_digging_filename,
               max_thickness=0.5,
               angles_of_attack_spec=op_def.aoa_spec,
               reynolds_numbers=op_def.reynolds_number,
               ncrits=op_def.ncrits,
               aoa_ld=op_def.aoa_ld,
               inv_min_drag_scaling=op_def.inv_min_drag_scaling,
               log=True)
else:
    logger.warn("There is a db digging file in the case folder, "
                "remove it to regenerate it")

# ------------------------------------------------------------------------------
# Graph characteristics / score vs geometry
# (max thickness, max thickness position)
# ------------------------------------------------------------------------------

thicknesses = list()
thickness_positions = list()
avg_max_l_to_d_angles = list()
avg_min_drags = list()
scores = list()

with open(op_def.db_digging_filename) as f:
    lines = f.readlines()

    for line in lines[8:-1]:
        if line.split(",")[12] == 'ok\n':
            thicknesses.append(float(line.split(",")[1]))
            thickness_positions.append(float(line.split(",")[2]))
            avg_max_l_to_d_angles.append(float(line.split(",")[6]))
            avg_min_drags.append(float(line.split(",")[7]))
            scores.append(float(line.split(",")[11]))

f, axarr = plt.subplots(2, 2)
# axarr[-1, -1].axis('off')  # hide bottom right subplot that is not used
axarr[0, 0].set_title("score = f(thickness)")
axarr[0, 1].set_title("score = f(max thickness position)")
axarr[1, 0].set_title("Avg max L/D angle = f(thickness)")
axarr[1, 1].set_title("Avg min drag = f(thickness)")
axarr[0, 0].scatter(thicknesses, scores, color="black")
axarr[0, 1].scatter(thickness_positions, scores, color="black")
axarr[1, 0].scatter(thicknesses, avg_max_l_to_d_angles, color="black")
axarr[1, 1].scatter(thicknesses, avg_min_drags, color="black")
# plt.gcf().suptitle(str("%s reynolds; %s ncrit" %
#                        (str(reynolds_number), str(ncrit))))
plt.show()
