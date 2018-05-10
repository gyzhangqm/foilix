# coding: utf-8

r"""DB api"""

import logging
import os
import sqlite3
import hashlib

logger = logging.getLogger(__name__)


def get_db_filename():
    r"""Avoid hardcoding the name all over the place"""
    # return os.path.join(os.path.dirname(__file__), "foilix_db.sqlite3")
    # return os.path.join(os.path.dirname(__file__),
    #                     "foilix_db_fed_with_find_coefficients.sqlite3")
    return os.environ["FOILIX_DB_SQLITE_PATH"]


def get_id_of_file(filepath, origin="Any"):
    r"""Retrieve the id of a section file given its name and its origin

    Parameters
    ----------
    filepath : str
        The path of the file
    origin : str
        Origin of the file (e.g. UIUC, Custom ...)

    Returns
    -------
    int
        The id in the section_file table

    """
    logger.debug("Filepath : %s" % filepath)
    try:
        file_content = open(filepath, 'rb').read()
    except IOError:
        return None
    if origin == "Any":
        with sqlite3.connect(get_db_filename()) as conn:
            cursor = conn.cursor()
            cursor.execute("""select id from section_file where file_name=? AND file_sha256=?""",
                           (os.path.basename(filepath),
                            hashlib.sha256(file_content).hexdigest()))
            return cursor.fetchone()[0]
    else:

        with sqlite3.connect(get_db_filename()) as conn:
            cursor = conn.cursor()
            cursor.execute("""select id from section_file where file_name=? AND file_sha256=? AND origin=?""",
                           (os.path.basename(filepath),
                            hashlib.sha256(file_content).hexdigest(),
                            origin))
            return cursor.fetchone()[0]


def get_id_of_source(source_name):
    r"""Id of a source given its name

    Parameters
    ----------
    source_name : str

    Returns
    -------
    int
        The id in the source table

    """
    with sqlite3.connect(get_db_filename()) as conn:
        cursor = conn.cursor()
        cursor.execute("""select id from source where name=?""", (source_name,))
        return cursor.fetchone()[0]
