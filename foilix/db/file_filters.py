#!/usr/bin/env python
# coding: utf-8

r"""Filter dat files"""


import os
import re
import logging

from foilix.foil import Foil


logger = logging.getLogger(__name__)


def symmetrical_dat_files(foil_data_folder):
    r"""Return a list of symmetrical dat files

    Parameters
    ----------
    foil_data_folder : str
        The path to the folder containing the 2d section dat files

    Returns
    -------
    list[str]
        List of dat file paths

    """

    logger.info("Listing symmetrical .dat files in %s" % foil_data_folder)

    # list of files with the .dat extension in the foil_data folder
    section_2d_files = [os.path.join(foil_data_folder, f)
                        for f in os.listdir(foil_data_folder)
                        if re.match(r".*\.dat", f)]
    logger.debug("%i section_2d_files" % len(section_2d_files))

    # List of symmetrical files in foil_data folder
    _symmetrical_dat_files = [f for f in section_2d_files
                              if Foil.from_dat_file(f).is_symmetrical() is True]

    logger.info("Found %i symmetrical files in %s" %
                (len(_symmetrical_dat_files), foil_data_folder))

    return _symmetrical_dat_files

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s :: %(levelname)6s :: %(module)20s '
                               ':: %(lineno)3d :: %(message)s')

    print(len(symmetrical_dat_files("../../foil_dat")))
