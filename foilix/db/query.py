#!/usr/bin/env python
# coding: utf-8

r"""Database data retrieval"""

import sqlite3

from foilix.db.api import get_id_of_file, get_db_filename


def aoas(section_file_path, reynolds, ncrit, mach=0.):
    r"""

    Parameters
    ----------
    section_file_path
    reynolds
    ncrit
    mach

    Returns
    -------
    aoas : list[tuple(float, int)] i.e.list[tuple(aoa, status)]
        aoas computed for reynolds, ncrit, mach

    """
    section_file_id = get_id_of_file(section_file_path)
    # print(section_file_id)
    with sqlite3.connect(get_db_filename()) as conn:
        cursor = conn.cursor()
        statement = """select aoa, status from data 
                       where section_file_id=? and 
                             reynolds=? and 
                             ncrit=? and 
                             mach=?"""
        cursor.execute(statement, (section_file_id, reynolds, ncrit, mach))
        return cursor.fetchall()


def data_from_db(section_file_path, aoa, reynolds, ncrit, mach=0.):
    r"""

    Parameters
    ----------
    section_file_path : str
        full path
    aoa : float
        The angle of attack
    reynolds : float
        The Reynolds number
    ncrit : float
        NCrit
    mach : float
        The Mach number

    Returns
    -------
    tuple(cl, cd, cdp, cm, top_xtr, bot_xtr) or None

    """
    # get the section file id
    # query the data table
    # return requested values
    section_file_id = get_id_of_file(section_file_path)
    # print(section_file_id)
    with sqlite3.connect(get_db_filename()) as conn:
        cursor = conn.cursor()
        statement = """select cl, cd, cdp, cm, top_xtr, bot_xtr, status 
                       from data 
                       where section_file_id=? and 
                             aoa=? and 
                             reynolds=? and 
                             ncrit=? and 
                             mach=?"""
        cursor.execute(statement, (section_file_id, aoa, reynolds, ncrit, mach))

        try:
            cl, cd, cdp, cm, top_xtr, bot_xtr, status = cursor.fetchone()
            if status == 1:
                return cl, cd, cdp, cm, top_xtr, bot_xtr
            else:
                return None
        except TypeError:
            return None


if __name__ == "__main__":
    import os
    print(aoas(os.path.join(os.environ["FOIL_DATA_FOLDER"], "hq07.dat"),
               30000,
               2.))
    print(aoas("../../foil_dat/hq07.dat", 30000, 2.))

    print(data_from_db(os.path.join(os.environ["FOIL_DATA_FOLDER"], "hq07.dat"),
                       2.,
                       30000,
                       2.,
                       0.))
    print(data_from_db("../../foil_dat/hq07.dat", 2., 30000, 2., 0.))

    cl, cd, cdp, cm, top_xtr, bot_xtr = data_from_db("../../foil_dat/hq07.dat",
                                                     aoa=2.,
                                                     reynolds=30000,
                                                     ncrit=2.,
                                                     mach=0.)
    print(cl)

    print(data_from_db("../../foil_dat/idonotexist.dat", 2., 30000, 2., 0.))

    print(data_from_db("../../foil_dat/hq07.dat", 2., 2000000000, 2., 0.))
