# coding: utf-8

r"""Script that deals with the foil data"""

from __future__ import absolute_import, print_function, division

import logging
import os
import re
import time
import multiprocessing
import numpy as np

from foilix.foil import Foil
from foilix.xfoil.polar import PolarMatrix
from foilix.optimization.scoring import yacht_appendage_scoring


logger = logging.getLogger(__name__)


def sort_foils_folder(foil_data_folder):
    r"""Separate file names related to symmetrical foils from file names
    related to unsymmetrical foils

    Parameters
    ----------
    foil_data_folder : str
        Path to the folder where the foil dat files are

    Returns
    -------
    tuple(list[str], list[str])
        (List of symmetrical foils file paths,
         list of unsymmetrical foils files paths)

    """
    # foil_data_folder = os.path.abspath(foil_data_folder)
    dat_files = [os.path.join(foil_data_folder, f)
                 for f in os.listdir(foil_data_folder)
                 if re.match(r".*\.dat", f)]
    foils = [Foil.from_dat_file(dt) for dt in dat_files]

    foils_symmetrical, foils_unsymmetrical = list(), list()

    for i, foil in enumerate(foils):
        if foil.is_symmetrical() is True:
            foils_symmetrical.append(dat_files[i])
        else:
            foils_unsymmetrical.append(dat_files[i])
    return foils_symmetrical, foils_unsymmetrical


# @timeout(60)
def compute(polar_matrix):
    r"""Call to polar_matrix.compute in a function
    that can be decorated by timeout

    This is now not strictly necessary since the data is retrieved
    from the database and not directly computed

    Parameters
    ----------
    polar_matrix : foilix.xfoil.polar.PolarMatrix

    """
    polar_matrix.compute()


def eval_foils(file_list,
               logfile_name,
               max_thickness,
               angles_of_attack_spec,
               reynolds_numbers,
               ncrits,
               aoa_ld,
               inv_min_drag_scaling=0.3,
               log=False):
    r"""Evaluate the foils from the foil dat files in file_list
    using yacht_appendage_scoring

    Parameters
    ----------
    file_list
    logfile_name : str
    max_thickness : float
        do not evaluate foils thicker than this
    angles_of_attack_spec : tuple(float)
        List of angles of attack for the polar matrix construction
        Max lift, max L/D may depend on this, especially of the upper value
        is too low
    reynolds_numbers : list[float]
    ncrits : list[float]
    aoa_ld : list[float]
        List of angles of attack for L/D evaluation
    inv_min_drag_scaling
    log : bool
        Write a log file?

    """
    start = time.time()
    results = list()

    nb_errors = 0

    if log is True:
        with open(logfile_name, "a") as f:
            f.write("Angles of attack,%s" % str(angles_of_attack_spec)+"\n")
            f.write("Reynolds numbers,%s" % str(reynolds_numbers)+"\n")
            f.write("ncrits,%s" % str(ncrits)+"\n")
            f.write("\n")
            f.write("aoa_ld,%s" % str(aoa_ld)+"\n")
            f.write("inv_min_drag_scaling,%s" % str(inv_min_drag_scaling)+"\n")
            f.write("\n")

            header = ["dat file",
                      "thickness",
                      "max_thickness_x",
                      "avg_max_lift",
                      "avg_max_lift_angle",
                      "avg_max_lift_to_drag",
                      "avg_max_lift_to_drag_angle",
                      "avg_min_drag",
                      "avg_min_drag_angle",
                      "avg l/d at aoa_ld angles",
                      "(1/avg_min_drag) / divider",
                      "global score",
                      "status"]
            f.write(",".join(header) + "\n")

    for i, foil_file in enumerate(file_list):
        logger.info("Handling : %s" % foil_file)
        logger.info("%i out of %i" % (i + 1, len(file_list)))

        try:
            foil = Foil.from_dat_file(foil_file)
            if foil.y_spread <= max_thickness:
                pm = PolarMatrix(foil_file,
                                 angles_of_attack_spec=angles_of_attack_spec,
                                 reynolds_numbers=reynolds_numbers,
                                 ncrits=ncrits,
                                 # use_db -> db must have been fed before
                                 use_db=True)
                compute(pm)

                logger.debug("pm.avg_max_lift : %s" % str(pm.avg_max_lift))
                avg_max_lift, avg_max_lift_angle = pm.avg_max_lift
                avg_max_lift_to_drag, avg_max_lift_to_drag_angle = \
                    pm.avg_max_lift_to_drag
                avg_min_drag, avg_min_drag_angle = pm.avg_min_drag

                result = [os.path.basename(foil_file),
                          foil.y_spread,
                          foil.max_y_x,
                          avg_max_lift,
                          avg_max_lift_angle,
                          avg_max_lift_to_drag,
                          avg_max_lift_to_drag_angle,
                          avg_min_drag,
                          avg_min_drag_angle,
                          # avg l/d at aoa_ld angles
                          sum([pm.avg_lift_to_drag(angle)
                               for angle in aoa_ld]) / len(aoa_ld),
                          (1 / avg_min_drag) * inv_min_drag_scaling,
                          yacht_appendage_scoring([pm.avg_lift_to_drag(angle)
                                                   for angle in aoa_ld],
                                                  avg_min_drag,
                                                  inv_min_drag_scaling),
                          "ok"]
                results.append(result)

        # IndexError had to be added following the switch
        # to PChip interpolation in Polar
        except (UnboundLocalError,
                TypeError,
                ValueError,
                RuntimeError,
                IndexError,
                multiprocessing.TimeoutError,
                np.linalg.linalg.LinAlgError) as e:
            result = [os.path.basename(foil_file),
                      foil.y_spread,
                      foil.max_y_x,
                      -1,
                      -1,
                      -1,
                      -1,
                      -1,
                      -1,
                      -1,
                      -1,
                      -1,
                      type(e).__name__]
            results.append(result)
            nb_errors += 1

        # finally:
        #     if len(result) > 0:
        #         results.append(result)

    # Display order based on some value (11 is global score)
    # results.sort(key=lambda x: -float(x[11]))
    # from operator import itemgetter
    sorted_results = sorted(results, key=lambda x: -float(x[11]))

    with open(logfile_name, "a") as f:
        for r in sorted_results:
            if len(r) > 0:
                f.write(",".join([str(item) for item in r])+"\n")

    total_time = time.time() - start
    logger.info("Took : %s s" % str(total_time))
    logger.info("%s s by foil on average" % str(total_time / len(file_list)))
    logger.info("There were %i errors" % nb_errors)
