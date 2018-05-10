#!/usr/bin/python
# coding: utf-8

r"""Add data to the database"""

import os
import re
import sqlite3
from hashlib import sha256
import multiprocessing
import logging
import thread
import math

from foilix.foil import Foil
from foilix.db.api import get_id_of_file, get_id_of_source
from foilix.db.api import get_db_filename
from foilix.xfoil.xfoil_aeropy import find_coefficients
from foilix.xfoil.xfoil import oper_visc_alpha
from foilix.db.file_filters import symmetrical_dat_files


logger = logging.getLogger(__name__)


def add_files(dat_files, origin_tag, write_db=True):
    r"""Add the dat files to the database
    (section_file and section_file_coords tables)

    Parameters
    ----------
    dat_files : list[str]
        List of file paths
    origin_tag : str
        Origin of the file (e.g. UIUC, Custom ...)
    write_db : bool
        if True, write to db
        if False, run but do not modify the db

    """
    for dat_file in dat_files:
        logger.info("Adding %s" % dat_file)
        print(dat_file)

        with open(dat_file) as df:
            nb = 0
            for line in df.readlines():
                if not line.startswith("#"):
                    items = re.findall(r'\S+', line)
                    if len(items) == 2:
                        try:
                            float(items[0])
                            float(items[1])
                            nb += 1
                        except ValueError:
                            print("---- %s --- %s" % (str(items[0]),
                                                      str(items[1])))
        foil = Foil.from_dat_file(dat_file)

        add_section_file_to_db(file_name=os.path.basename(dat_file),
                               file_sha256=sha256(open(dat_file, 'rb').read()).hexdigest(),
                               origin=origin_tag,
                               nb_points=nb,
                               is_symmetrical=foil.is_symmetrical,
                               max_thickness=foil.y_spread if foil.is_symmetrical else -1,
                               max_thickness_x=foil.max_y_x if foil.is_symmetrical else -1,
                               le_radius=foil.pseudo_leading_edge_radius,
                               closed_te=foil.has_closed_te,
                               points=foil.points,
                               write_db=write_db)


def add_section_file_to_db(file_name,
                           file_sha256,
                           origin,
                           nb_points,
                           is_symmetrical,
                           max_thickness,
                           max_thickness_x,
                           le_radius,
                           closed_te,
                           points,
                           write_db=True):
    r"""Add a section file to the database

    Parameters
    ----------
    file_name : str
        Foil section file name
    file_sha256 : str
        Foil section file hash
    origin : str
    nb_points : int
        Number of points that define the section
    is_symmetrical : bool
    max_thickness : float
    max_thickness_x : float
    le_radius : float
    closed_te : bool
    points : list[tuple(x, y)]
    write_db : bool, optional (default is true)

    """

    logger.info("Adding %s" % file_name)

    if write_db:

        with sqlite3.connect(get_db_filename()) as conn:
            cursor = conn.cursor()

            # add the section file to section_file

            cursor.execute("""insert into section_file (file_name,
                                                        file_sha256,
                                                        origin,
                                                        nb_points,
                                                        is_symmetrical,
                                                        max_thickness,
                                                        max_thickness_x,
                                                        le_radius,
                                                        closed_te) 
                            values (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                           (file_name,
                            file_sha256,
                            origin, nb_points,
                            1 if is_symmetrical is True else 0,
                            max_thickness,
                            max_thickness_x,
                            le_radius,
                            1 if closed_te is True else 0))

            section_file_id = cursor.lastrowid

            # add the points to section_file_coords
            for i, point in enumerate(points):
                x, y = point
                cursor.execute("""insert into section_file_coords (section_file_id,
                                                                   point_order,
                                                                   x,
                                                                   y)
                values (?, ?, ?, ?)""", (section_file_id, i, x, y))


def add_xfoil_data_of_file_list(dat_files,
                                origin,
                                aoas,
                                rns,
                                ncrits,
                                source_name="Xfoil",
                                write_db=True):
    r"""Compute the data and add to db for a list of dat files

    Parameters
    ----------
    dat_files : list[str]
        List of paths to dat files
    origin : str
    aoas : list[float]
    rns : list[float]
    ncrits : list[float]
    source_name : str, optional
        Name of source, default is Xfoil
    write_db : bool
        if True, write to db
        if False, run but do not modify the db

    """
    for dat_file in dat_files:
        logger.info("Adding data for file : %s" % dat_file)
        try:
            add_xfoil_data_of_file(dat_file,
                                   origin,
                                   aoas,
                                   rns,
                                   ncrits,
                                   source_name=source_name,
                                   write_db=write_db)
        except multiprocessing.TimeoutError:
            logger.error("TimeoutError for %s %s %s %s" % (dat_file,
                                                           str(aoas),
                                                           str(rns),
                                                           str(ncrits)))
        except thread.error:
            logger.error("thread.error for %s %s %s %s" % (dat_file,
                                                           str(aoas),
                                                           str(rns),
                                                           str(ncrits)))
        except AttributeError:
            logger.error("AttributeError for %s %s %s %s" % (dat_file,
                                                             str(aoas),
                                                             str(rns),
                                                             str(ncrits)))


def add_xfoil_data_of_file(filepath,
                           origin,
                           aoas,
                           rns,
                           ncrits,
                           source_name="Xfoil",
                           write_db=True,
                           method="oper_visc_alpha"):
    r"""Run Xfoil to get data, add the data to the database

    Parameters
    ----------
    filepath : str
        Path to a dat file
    origin : str
    aoas : list[float]
    rns : list[float]
    ncrits : list[float]
    source_name : str, optional
        Name of source, default is Xfoil
    write_db : bool
        if True, write to db
        if False, run but do not modify the db
    method : str
        find_coefficients (xfoil_module.py)
        or
        oper_visc_alpha (xfoil.py) - cannot be timeout(ed)

    """
    logger.info("Dealing with : %s" % filepath)
    # id of file
    section_file_id = get_id_of_file(filepath, origin)
    source_id = get_id_of_source(source_name)
    # (recreate dat from db?)
    # evaluate for specs
    with sqlite3.connect(get_db_filename()) as conn:
        cursor = conn.cursor()
        for rn in rns:
            for nc in ncrits:
                for aoa in aoas:
                    if method == "find_coefficients":
                        try:
                            os.chdir(os.path.join(os.path.dirname(__file__),
                                                  "../../foilix/xfoil"))

                            data = find_coefficients(filepath,
                                                     aoa,
                                                     reynolds=rn,
                                                     ncrit=nc,
                                                     is_naca=False,
                                                     iteration=200)
                            logger.debug("Data value : %s" % str(data.values()))
                            for value in data.values():
                                if math.isnan(value):
                                    raise ValueError
                            assert aoa == data['alpha']
                            # TODO : check the enreg does not exist
                            if write_db:
                                cursor.execute("""insert into data (section_file_id,
                                                                    aoa,
                                                                    reynolds,
                                                                    ncrit,
                                                                    mach,
                                                                    status,
                                                                    cl,
                                                                    cd,
                                                                    cdp,
                                                                    cm,
                                                                    top_xtr,
                                                                    bot_xtr,
                                                                    source_id) 
                                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """,
                                               (section_file_id,
                                                aoa,
                                                rn,
                                                nc,
                                                0.,
                                                1,
                                                data['CL'],
                                                data['CD'],
                                                data['CDp'],
                                                data['CM'],
                                                data['Top_Xtr'],
                                                data['Bot_Xtr'],
                                                source_id))
                        except IndexError:
                            logger.debug("Inserting default record "
                                         "(IndexError)")
                            cursor.execute("""insert into data (section_file_id,
                                                                aoa,
                                                                reynolds,
                                                                ncrit,
                                                                mach,
                                                                status,
                                                                source_id) 
                                            values (?, ?, ?, ?, ?, ?, ?)""",
                                           (section_file_id,
                                            aoa,
                                            rn,
                                            nc,
                                            0.,
                                            0,
                                            source_id))
                        except IOError:
                            logger.debug("Inserting default record (IOError)")
                            cursor.execute("""insert into data (section_file_id,
                                                                aoa,
                                                                reynolds,
                                                                ncrit,
                                                                mach,
                                                                status,
                                                                source_id) 
                                            values (?, ?, ?, ?, ?, ?, ?)""",
                                           (section_file_id,
                                            aoa,
                                            rn,
                                            nc,
                                            0.,
                                            0,
                                            source_id))
                        except ValueError:
                            logger.debug("Inserting default record "
                                         "(ValueError)")
                            cursor.execute("""insert into data (section_file_id,
                                                                aoa,
                                                                reynolds,
                                                                ncrit,
                                                                mach,
                                                                status,
                                                                source_id) 
                                            values (?, ?, ?, ?, ?, ?, ?)""",
                                           (section_file_id,
                                            aoa,
                                            rn,
                                            nc,
                                            0.,
                                            0,
                                            source_id))
                        except multiprocessing.TimeoutError:
                            logger.debug("Inserting default record "
                                         "(multiprocessing.TimeoutError)")
                            cursor.execute("""insert into data (section_file_id,
                                                                aoa,
                                                                reynolds,
                                                                ncrit,
                                                                mach,
                                                                status,
                                                                source_id) 
                                            values (?, ?, ?, ?, ?, ?, ?)""",
                                           (section_file_id,
                                            aoa,
                                            rn,
                                            nc,
                                            0.,
                                            0,
                                            source_id))

                    elif method == "oper_visc_alpha":  # method oper_visc_alpha
                        data_array, data_header, infodict, warnings = \
                            oper_visc_alpha(filepath,
                                            aoa,
                                            rn,
                                            iterlim=2000,
                                            show_seconds=0,
                                            n_crit=nc)
                        there_is_a_nan = False
                        if len(data_array) > 0:
                            data = data_from_xfoil_data_array(data_array)

                            for value in data:
                                if math.isnan(value):
                                    there_is_a_nan = True

                        if len(data_array) > 0 and there_is_a_nan is False:
                            aoa_da, cl, cd, cdp, cm, top_xtr, bot_xtr = data
                            assert aoa == aoa_da
                            # TODO : check the enreg does not exist
                            if write_db:
                                cursor.execute("""insert or replace into data  
                                                            (section_file_id,
                                                            aoa,
                                                            reynolds,
                                                            ncrit,
                                                            mach,
                                                            status,
                                                            cl,
                                                            cd,
                                                            cdp,
                                                            cm,
                                                            top_xtr,
                                                            bot_xtr,
                                                            source_id) values
                                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                               (section_file_id,
                                                aoa,
                                                rn,
                                                nc,
                                                0.,
                                                1,
                                                cl,
                                                cd,
                                                cdp,
                                                cm,
                                                top_xtr,
                                                bot_xtr,
                                                source_id))
                        else:
                            with open("feed_db_errors.csv", "a") as f:
                                f.write("%s,%s,%s,%s\n" % (filepath,
                                                           str(aoa),
                                                           str(rn),
                                                           str(nc)))
                            if write_db:
                                cursor.execute("""insert or replace into data 
                                                            (section_file_id,
                                                            aoa,
                                                            reynolds,
                                                            ncrit,
                                                            mach,
                                                            status,
                                                            source_id) values 
                                (?, ?, ?, ?, ?, ?, ?)""",
                                               (section_file_id,
                                                aoa,
                                                rn,
                                                nc,
                                                0.,
                                                0,
                                                source_id))
                    else:
                        raise ValueError


def data_from_xfoil_data_array(data_array):
    r"""Retrieve data from a Xfoil data array

    Parameters
    ----------
    data_array : list[list[float]]

    """
    if len(data_array) != 1:
        raise AssertionError
    if len(data_array[0]) != 7:
        raise AssertionError
    aoa = data_array[0, 0]
    cl = data_array[0, 1]
    cd = data_array[0, 2]
    cdp = data_array[0, 3]
    cm = data_array[0, 4]
    top_xtr = data_array[0, 5]
    bot_xtr = data_array[0, 6]

    return aoa, cl, cd, cdp, cm, top_xtr, bot_xtr


def main(add_sections, add_data, aoas, reynolds, ncrits):
    r"""Main function for feeding the DB

    Parameters
    ----------
    add_sections : bool
        Should sections be added to the section_* tables of the db
    add_data : bool
        Should the data be computed and added to the db
    aoas
    reynolds
    ncrits

    """

    # TODO : some foils actually do not come from the UIUC database

    # list of files with the .dat extension in the foil_data folder
    foil_data_folder = "../../foil_dat"
    symmetrical_dat_files_ = symmetrical_dat_files(foil_data_folder)

    # Drela almost symmetrical files
    drela_almost_symmetrical_dat_files = ['ht05.dat',
                                          'ht08.dat',
                                          'ht12.dat',
                                          'ht13.dat',
                                          'ht14.dat']
    drela_almost_symmetrical_dat_files = [os.path.join(foil_data_folder, f)
                                          for f
                                          in drela_almost_symmetrical_dat_files]
    # drela_unsymmetrical_dat_files = ['../../foil_data/ht22.dat',
    #                                  '../../foil_data/ht23.dat']

    # G Florent sections
    gf_dat_files = ['gf_0003.dat']
    gf_dat_files = [os.path.join(foil_data_folder, f) for f in gf_dat_files]

    # Add the files to the DB
    if add_sections:
        # add_files(symmetrical_dat_files_, "UIUC")
        # add_files(drela_almost_symmetrical_dat_files, "Drela")
        add_files(gf_dat_files, "GFlorent")

    # Add the data to the DB
    if add_data:
        for aoa in aoas:
            logger.info("Adding data for aoa : %f" % aoa)
            # add_xfoil_data_of_file_list(symmetrical_dat_files_, "Any",
            #                             aoas=[aoa],
            #                             rns=reynolds,
            #                             ncrits=ncrits,
            #                             source_name="Xfoil")

            # add_xfoil_data_of_file_list(drela_almost_symmetrical_dat_files,
            #                             "Any",
            #                             aoas=[aoa],
            #                             rns=reynolds,
            #                             ncrits=ncrits,
            #                             source_name="Xfoil")

            add_xfoil_data_of_file_list(gf_dat_files, "Any",
                                        aoas=[aoa],
                                        rns=reynolds,
                                        ncrits=ncrits,
                                        source_name="Xfoil")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s :: %(levelname)6s :: %(module)20s '
                               ':: %(lineno)3d :: %(message)s')

    # If only computing other aos, rns ... do not add the sections again
    # The behaviour for data is to overwrite(insert or replace)

    reynolds = [5e3, 1e4, 1.5e4, 2e4, 2.5e4, 3e4, 3.5e4, 4e4, 4.5e4, 5e4, 5.5e4,
                6e4, 6.5e4, 7e4, 7.5e4, 8e4, 8.5e4, 9e4, 9.5e4, 1e5]

    main(add_sections=True,
         add_data=True,
         aoas=[0., 1., 2., 3., 4., 5., 6., 7., 8., 9., 10.],
         reynolds=reynolds,
         ncrits=[1., 1.5, 2., 2.5, 3.0])
