#!/usr/bin/env python
# coding: utf-8

r"""Detect files that contain less points than a threshold to define sections"""

import logging
import re

from foilix.filters import symmetrical_dat_files

logger = logging.getLogger(__name__)


def sanity_check(foil_dat_folder, nb_points_threshold=60):
    r"""

    Parameters
    ----------
    foil_dat_folder : str
    nb_points_threshold : int

    Returns
    -------

    """
    i = 0
    sdat = symmetrical_dat_files(foil_dat_folder=foil_dat_folder)
    for f in sdat:
        valid_lines = 0
        with open(f) as f_:
            lines = f_.readlines()
            for line in lines:
                items = re.findall(r'\S+', line)
                if len(items) == 2:
                    try:
                        float(items[0])
                        float(items[1])
                        valid_lines += 1
                    except (TypeError, ValueError):
                        logger.debug("Found a line that does not define a "
                                     "point")

            logger.info("%s has %i points" % (f, valid_lines))

            if valid_lines < nb_points_threshold:
                logger.warning("%s only has %i points" % (f, valid_lines))
                i += 1
    logger.info("Found %i .dat files out of %i with less than %i points" %
                (i, len(sdat), nb_points_threshold))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s :: %(levelname)6s :: %(module)20s '
                               ':: %(lineno)3d :: %(message)s')

    sanity_check("../foil_dat", nb_points_threshold=60)
