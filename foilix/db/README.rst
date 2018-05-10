Pre-requisites
--------------

The db file is defined by the FOILIX_DB_SQLITE_PATH environment variable

Procedure
---------

create_foilix_db.py
 create the db and basic content

repanel.py (optional) - Currently broken (the generated files are empty)
    repanel (symmetrical) foils

feed_db.py [Run before going to sleep]
    add section files to db
    run xfoil to compute the values

    WARNING : When running feed_db after the initial run, make sure not to overwrite the sections enregs by using a different dataset.
    This would corrupt the whole db (e.g. another section being associated to another dataset by changing its id while not recomputing the data)

    depending on the method parameter of add_xfoil_data_of_file(), the values will be computed using
    oper_visc_alpha (xfoil.py) or find_coefficients(xfoil_module.py (from aeropy))

    The find_coefficients(xfoil_module.py (from aeropy)) does not currently work and has to be fixed (call to PACC,
    then filename should create a fle por polar accumulation, but the file s not there)

DBs
---

The current db is foilix_db.sqlite3

The other sqlite3 file should be considered as experiments

