#!/usr/bin/env python
# coding: utf-8

r"""Step 1 of the global process of optimizing a 2D foil section

Find the best 2D sections in precomputed data for the defined problem.
The output of this step is a CSV file where the 2D sections are ranked
from best (score) to worst

"""

from os import getcwd
from os.path import join, isfile
import logging
import matplotlib
from matplotlib import pyplot as plt

from corelib.core.files import p_

from foilix.foils_eval import eval_foils
from foilix.filters import sort_foils_folder
from foilix.read_config import read_config

data_digging_csv_file = join(getcwd(), "data_digging.csv")


def dig():
    config = read_config(join(getcwd(), "foilix_case.conf"))

    # The presence of the data digging results file blocks re-execution
    if not isfile(data_digging_csv_file):
        # ------------------------------------------------------------------
        # Evaluate foils in database with scoring / find the best candidates
        # ------------------------------------------------------------------
        symmetrical_sections_filepaths, _ = \
            sort_foils_folder(config["foil_dat_folder"])
        logger.info("There are %i symmetrical foils in the foils database" %
                    len(symmetrical_sections_filepaths))
        for p in symmetrical_sections_filepaths:
            print(p)
        print("%i symmetrical sections" % len(symmetrical_sections_filepaths))

        # add the almost symmetrical Drela foils
        # (ht22 and ht23 are not symmetrical at all)
        symmetrical_sections_filepaths.append(join(config["foil_dat_folder"],
                                                   'ht05.dat'))
        symmetrical_sections_filepaths.append(join(config["foil_dat_folder"],
                                                   'ht08.dat'))
        symmetrical_sections_filepaths.append(join(config["foil_dat_folder"],
                                                   'ht12.dat'))
        symmetrical_sections_filepaths.append(join(config["foil_dat_folder"],
                                                   'ht13.dat'))
        symmetrical_sections_filepaths.append(join(config["foil_dat_folder"],
                                                   'ht14.dat'))

        # eval_foil uses the yacht_appendage_scoring function
        eval_foils(foil_data_folder=config["foil_data_folder"],
                   file_list=symmetrical_sections_filepaths,
                   logfile_name=data_digging_csv_file,
                   max_thickness=0.5,
                   angles_of_attack_spec=config["aoa_spec"],
                   reynolds_numbers=config["reynolds_numbers"],
                   ncrits=config["ncrits"],
                   aoa_ld=config["aoa_ld"],
                   inv_min_drag_scaling=config["inv_min_drag_scaling"],
                   log=True)
    else:
        logger.warning("There is a db digging file in the case folder, "
                       "remove it to regenerate it")


def plot():
    r"""Graph characteristics / score vs geometry
    (max thickness, max thickness position)"""

    # Set the matplotlib rc_context from file
    MATPLOTLIBRC = p_(__file__, 'matplotlibrc_defaults')
    matplotlib.rc_context(fname=MATPLOTLIBRC)

    thicknesses = list()
    thickness_positions = list()
    avg_max_l_to_d_angles = list()
    avg_min_drags = list()
    scores = list()

    with open(data_digging_csv_file) as f:
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

if __name__ == "__main__":
    import sys
    if not (sys.version_info[0] >= 3 and sys.version_info[1] >= 6):
        msg = "foilix data digging requires at least Python 3.6 (uses libra)"
        raise EnvironmentError(msg)

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s :: %(levelname)6s :: %(module)20s '
                               ':: %(lineno)3d :: %(message)s')
    logger = logging.getLogger(__name__)

    dig()
    plot()
