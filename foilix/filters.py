#!/usr/bin/env python
# coding: utf-8

r"""Filter dat files"""


import os
import re
import logging

from foilix.foil import Foil


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


def symmetrical_dat_files(foil_dat_folder):
    r"""Return a list of symmetrical dat files

    Parameters
    ----------
    foil_dat_folder : str
        The path to the folder containing the 2d section dat files

    Returns
    -------
    list[str]
        List of dat file paths

    """

    logger.info("Listing symmetrical .dat files in %s" % foil_dat_folder)

    # list of files with the .dat extension in the foil_data folder
    section_2d_files = [os.path.join(foil_dat_folder, f)
                        for f in os.listdir(foil_dat_folder)
                        if re.match(r".*\.dat", f)]
    logger.debug("%i section_2d_files" % len(section_2d_files))

    # List of symmetrical files in foil_data folder
    _symmetrical_dat_files = [f for f in section_2d_files
                              if Foil.from_dat_file(f).is_symmetrical() is True]

    logger.info("Found %i symmetrical files in %s" %
                (len(_symmetrical_dat_files), foil_dat_folder))

    return _symmetrical_dat_files

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s :: %(levelname)6s :: %(module)20s '
                               ':: %(lineno)3d :: %(message)s')

    print(len(symmetrical_dat_files("../../foil_dat")))
