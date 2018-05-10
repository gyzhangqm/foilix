#!/usr/bin/env python
# coding: utf-8

r"""database creation and initial data"""

from __future__ import print_function

import logging
import os
import sqlite3

from foilix.db.api import get_db_filename

logger = logging.getLogger(__name__)


def create_foilix_db():
    r"""Creates the foilix db without feeding it with any data"""

    # db_filename = "foilix_db.sqlite3"
    schema_filename = 'foilix_schema.sql'

    db_is_new = not os.path.exists(get_db_filename())

    logger.info("Creating DB : %s" % get_db_filename())
    logger.info("  DB is new : %s" % str(db_is_new))

    with sqlite3.connect(get_db_filename()) as conn:
        if db_is_new:
            with open(schema_filename, 'rt') as f:

                # schema from foilix_schema.sql
                schema = f.read()
                conn.executescript(schema)
                cursor = conn.cursor()

                # Initial data
                cursor.execute("""insert into source_type (name, description) 
                               values ('simulation', 'Any simulation')""")
                simulation_id = cursor.lastrowid
                cursor.execute("""insert into source (name,
                                                      description,
                                                      source_type_id) 
                                                      values (?, ?, ?)""",
                               ("Xfoil",
                                "Xfoil run",
                                simulation_id))
                cursor.execute("""insert into source_type (name, description) 
                               values ('experiment', 'Any experiment')""")
                experiment_id = cursor.lastrowid
        else:
            logger.warning('Database exists, assume schema does, too.')


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s :: %(levelname)6s :: %(module)20s '
                               ':: %(lineno)3d :: %(message)s')

    create_foilix_db()
