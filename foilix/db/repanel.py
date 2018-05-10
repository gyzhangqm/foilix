#!/usr/bin/env python
# coding: utf-8

r"""Repanel the symmetrical dat files in foil_dat with 281 points

The repanelled section are stored in a file with __p__281 
appended to the file name:
*.dat -> *__p__281.dat

"""

import os
from time import sleep
import logging

from foilix.db.file_filters import symmetrical_dat_files
from foilix.xfoil.xfoil import Xfoil


logger = logging.getLogger(__name__)


def repanel(datfile_name, nb_panels):
    r"""Change the number of definition points for the 2d section

    The results are saved in filename__p__<nb_panels>.dat

    Parameters
    ----------
    datfile_name : str
        relative filepath to the original dat file
        e.g. : '../../foil_dat/ys900.dat'
    nb_panels : int
        The number of definition points

    Returns
    -------

    """
    xfoil_exe_dir = os.path.join(os.path.dirname(__file__),
                                 "../../foilix/xfoil")
    # assert os.path.isfile(os.path.join(xfoil_exe_dir, "xfoil.exe"))
    assert os.path.isfile(datfile_name)
    # os.chdir(xfoil_exe_dir)
    with Xfoil(xfoil_exe_dir) as xf:
        logger.debug("Loading : %s" % datfile_name)

        # load from file
        xf.cmd('LOAD {}\n\n'.format(datfile_name), autonewline=False)
        logger.debug("Issuing repanelling commands")
        xf.cmd('PPAR\nN\n%s\n\n' % str(nb_panels), autonewline=False)
        # xf.cmd('N')  # Change number of panel for
        #                                      repaneling (xfoil default is 160)
        # xf.cmd(str(nb_panels))  # odd number is better
        # xf.cmd('')
        # xf.cmd('')

        # enter GDES menu
        xf.cmd('GDES\nCADD\n\n\n\n\nPANEL\n', autonewline=False)

        # add points at corners
        # xf.cmd('CADD')

        # accept default input - Corner angle criterion for refinement(deg)
        # xf.cmd('')

        # accept default input - Type of spline parameter (1: uniform,
        #                                                  2: arclength)
        # xf.cmd('')

        # accept default input - Refinement x limits -0.1 -> 1.1
        # xf.cmd('')

        # accept default input
        # xf.cmd('')

        # regenerate paneling
        # xf.cmd('PANEL')

        # xf.cmd('SAVE')
        datfile_dir = os.path.dirname(datfile_name)
        name, extension = os.path.splitext(os.path.basename(datfile_name))
        new_name = "%s/%s" % (datfile_dir,
                              name + "__p__" + str(nb_panels) + extension)
        xf.cmd('SAVE')
        xf.cmd(new_name)

        # For some reason, the repanelled file does not get created
        # without the following line
        # 0.1s is not enough ...
        sleep(0.2)

        # In case there is already a file with that name, it will replace it.
        # The yes stands for YES otherwise Xfoil will do nothing with it.
        xf.cmd('Y')

        # From xfoil
        xf.cmd('QUIT')


def do_repanel_symmetrical(foil_data_folder, nb_panels):
    r"""Repanel the files that are considered symmetrical

    Parameters
    ----------
    foil_data_folder : str
        The path to the folder containing the 2d section dat files
    nb_panels : int
        The number of panels

    """
    i, j = 0, 0

    for f in symmetrical_dat_files(foil_data_folder):
        repanel(f, nb_panels=nb_panels)
        i += 1

    logger.info("Repanelled %i symmetrical foil sections with %i panels" %
                (i, nb_panels))

    # handle missed Drela files
    for f in ["%s/%s" % (foil_data_folder, f) for f in ["ht05.dat",
                                                        "ht08.dat",
                                                        "ht12.dat",
                                                        "ht13.dat",
                                                        "ht14.dat"]]:
        repanel(f, nb_panels=nb_panels)
        j += 1

    logger.info("Repanelled %i almost symmetrical foil sections "
                "with %i panels" % (j, nb_panels))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s :: %(levelname)6s :: %(module)20s '
                               ':: %(lineno)3d :: %(message)s')

    # xfoil_exe_dir = os.path.join(os.path.dirname(__file__),
    #                              "../../foilix/xfoil")

    # os.chdir(xfoil_exe_dir)
    # print(os.getcwd())
    # logger.info("Changing CWD to %s" % xfoil_exe_dir)
    # assert os.path.isfile(os.path.join(xfoil_exe_dir, "xfoil.exe"))

    # do_repanel_symmetrical(foil_data_folder=os.environ["FOIL_DATA_FOLDER"],
    #                        nb_panels=281)

    do_repanel_symmetrical(foil_data_folder="../../foil_dat", nb_panels=281)
    # repanel("../../foil_data/2032c.dat", nb_panels=281)

    # Just to check the file was created ...
    # assert os.path.isfile(os.path.join(os.path.dirname(__file__),
    #                                    "../../foil_data/2032c__p__281.dat"))

    # rollback()
