#!/usr/bin/env python
# coding: utf-8

r"""Rollback the repanelling"""

import logging
import os


logger = logging.getLogger(__name__)


def rollback():
    r"""Revert the effects of do_repanel.
    i.e. delete dat files created by do_repanel()"""
    i = 0
    for f in os.listdir(os.environ["FOIL_DATA_FOLDER"]):
        if "__p__" in f:
            os.remove(os.path.join(os.environ["FOIL_DATA_FOLDER"], f))
            i += 1

    logger.info("Removed %i repanelled files" % i)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s :: %(levelname)6s :: %(module)20s '
                               ':: %(lineno)3d :: %(message)s')

    rollback()
