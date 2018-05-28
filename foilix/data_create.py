# coding: utf-8

import logging

import numpy as np

from corelib.core.files import p_
from corelib.core.timeout import timeout
from corelib.core.profiling import timeit

from foilix.xfoil.xfoil import oper_visc_alpha

# Python 2 compatibility.
try:
    TimeoutError
except NameError:
    TimeoutError = RuntimeError

logger = logging.getLogger(__name__)

# avoid spaces in error messages
error_messages = {u' WARNING: Poor input coordinate distribution\n': "poor_input_coordinate_distribution"}


def create_data(foil_id,
                ncrits,
                reynoldss,
                machs,
                aoas,
                iterlim=200,
                formats=None):
    r"""Create the files containing the data
    
    Parameters
    ----------
    foil_id : str
    ncrits : list
    reynoldss : list
    machs : list
    aoas : list
        xfoil format (start, end, step) specification of angles of attack
    iterlim : int
    formats : list
        List of output formats

    """
    if formats is None:
        formats = ["csv", "ndf"]

    header = {"csv": "mach,ncrit,reynolds,aoa,cl,cd,cdp,cm,top_xtr,bot_xtr,warnings\n",
              "ndf": "0 0 0 0 2 2 2 2 2 2\n"
                     "mach ncrit reynolds aoa cl cd cdp cm top_xtr bot_xtr\n"}

    # values are (format, nb items in format) tuples
    line_format = {"csv": ("%.2f,%.2f,%.1f,%.2f,%f,%f,%f,%f,%f,%f,%s", 11),
                   "ndf": ("%.2f %.2f %.1f %.2f %f %f %f %f %f %f", 10)}

    foil_data_file = {"csv": p_(__file__, "../foil_data/%s.csv" % foil_id),
                      "ndf": p_(__file__, "../foil_data/%s.ndf" % foil_id)}

    write_error_lines = {"csv": True, "ndf": False}

    for format_ in formats:
        with open(foil_data_file[format_], 'w') as f:
            f.write(header[format_])

    for mach in machs:
        for ncrit in ncrits:
            for reynolds in reynoldss:
                try:
                    results = get_data(foil_id,
                                       ncrit,
                                       reynolds,
                                       mach,
                                       aoas,
                                       iterlim=iterlim)

                    for i, aoa in enumerate(
                            np.arange(aoas[0],
                                      aoas[1] + aoas[2] / 2.,
                                      aoas[2])):
                        # is the answer in results?
                        record = [r for r in results if r[0] == aoa]
                        if len(record) == 1:
                            a, cl, cd, cdp, cm, top_xtr, bot_xtr, warnings = \
                                record[0]
                            # Goal of the following lines is to replace a
                            # warning with spaces by a warning without spaces
                            # spaces are not good for later use of data files !
                            new_warnings = []
                            for w in warnings:
                                try:
                                    new_warnings.append(error_messages[w])
                                except KeyError:
                                    new_warnings.append(w)
                            for format_ in formats:
                                data_line = line_format[format_][0] % (mach,
                                                                       ncrit,
                                                                       reynolds,
                                                                       aoa,
                                                                       cl,
                                                                       cd,
                                                                       cdp,
                                                                       cm,
                                                                       top_xtr,
                                                                       bot_xtr,
                                                                       str(new_warnings))[:line_format[format_][1]]
                                # print(data_line)
                                with open(foil_data_file[format_], 'a') as f:
                                    f.write("%s\n" % data_line)
                        else:
                            if len(record) > 1:
                                msg = "aoa twice or more results !!"
                                raise AssertionError(msg)

                            a, cl, cd, cdp, cm, top_xtr, bot_xtr, warnings = \
                                (aoa,
                                 float('nan'),
                                 float('nan'),
                                 float('nan'),
                                 float('nan'),
                                 float('nan'),
                                 float('nan'),
                                 ["could_not_be_computed"])

                            for format_ in formats:
                                data_line = line_format[format_][0] % (mach,
                                                                       ncrit,
                                                                       reynolds,
                                                                       aoa,
                                                                       cl,
                                                                       cd,
                                                                       cdp,
                                                                       cm,
                                                                       top_xtr,
                                                                       bot_xtr,
                                                                       str(warnings))[:line_format[format_][1]]
                                # print(data_line)
                                if write_error_lines[format_] is True:
                                    with open(foil_data_file[format_], 'a') as f:
                                        f.write("%s\n" % data_line)
                except TimeoutError:
                    msg = "%s timedout for mach: %f, ncrit: %f, " \
                          "reynolds: %f" % (foil_id, mach, ncrit, reynolds)
                    logger.error(msg)
                    for i, aoa in enumerate(
                            np.arange(aoas[0],
                                      aoas[1] + aoas[2] / 2.,
                                      aoas[2])):
                        a, cl, cd, cdp, cm, top_xtr, bot_xtr, warnings = \
                            (aoa,
                             float('nan'),
                             float('nan'),
                             float('nan'),
                             float('nan'),
                             float('nan'),
                             float('nan'),
                             ["timedout"])
                        for format_ in formats:
                            data_line = line_format[format_][0] % (mach,
                                                                   ncrit,
                                                                   reynolds,
                                                                   aoa,
                                                                   cl,
                                                                   cd,
                                                                   cdp,
                                                                   cm,
                                                                   top_xtr,
                                                                   bot_xtr,
                                                                   str(warnings))[:line_format[format_][1]:]
                            # print(data_line)
                            if write_error_lines[format_] is True:
                                with open(foil_data_file[format_], 'a') as f:
                                    f.write("%s\n" % data_line)


@timeout(60)
def get_data(foil_id, ncrit, reynolds, mach, aoas, iterlim=200):
    r"""
    
    Parameters
    ----------
    foil_id : str
        Foil name, i.e. the file name of the dat file without the dat extension
    ncrit : float
        ncrit, a low value is for a medium with high turbulence
               a high value if for a medium with low turbulence
    reynolds : float
        The Reynolds number
    mach : float
        Mach number
    aoas : list
        xfoil format (start, end, step) specification of angles of attack
    iterlim : int, optional
        Limit number of iterations

    Returns
    -------
    list of tuples : [(alpha, cl, cd, cdp, cm, top_xtr, bot_xtr, warnings), ...]

    """
    data_array, data_header, infodict, warnings = \
        oper_visc_alpha("../foil_dat/%s.dat" % foil_id,
                        aoas,
                        reynolds,
                        mach=mach,
                        iterlim=iterlim,
                        show_seconds=None,
                        n_crit=ncrit)
    results = []

    for d in data_array:
        # try:
        alpha = d[0]
        cl = d[1]
        cd = d[2]
        cdp = d[3]
        cm = d[4]
        top_xtr = d[5]
        bot_xtr = d[6]

        results.append((alpha, cl, cd, cdp, cm, top_xtr, bot_xtr, warnings))

        # except IndexError:  # probably no convergence
        #     msg = "data_array is empty (foil_id: %s, aoas:%s, ncrit: %.2f, " \
        #           "reynolds:%.1f, mach: %.1f" % (foil_id,
        #                                          str(aoas),
        #                                          ncrit,
        #                                          reynolds,mach)
        #     logger.error(msg)

    return results

if __name__ == "__main__":
    # TODO: essayer des position de turbulateurs
    #       -> inclure aux données (e.g. à 10 %, 20 % ..)
    import time
    from os.path import basename, splitext
    from foilix.filters import sort_foils_folder
    from corelib.core.python_ import py3
    import pandas as pd

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s :: %(levelname)6s :: %(module)20s '
                               ':: %(lineno)3d :: %(message)s')

    if py3() is False:
        sym, asym = sort_foils_folder("../foil_dat")
        sym_foil_ids = [splitext(basename(p))[0] for p in sym]
        sym_foil_ids.append("ht05")
        sym_foil_ids.append("ht08")
        sym_foil_ids.append("ht12")
        sym_foil_ids.append("ht13")
        sym_foil_ids.append("ht14")

        logger.info("Processing %i symmetrical foils" % len(sym_foil_ids))

        if True:
            for foil_id in sym_foil_ids:
                logger.info("Processing %s" % foil_id)
                create_data(foil_id,
                            ncrits=[1., 2., 3., 4.],
                            # reynoldss=[5e4, 1e5, 1.5e5, 2e5],
                            reynoldss=np.arange(5e3, 3e5 + 1, 5e3),
                            machs=[0.],
                            aoas=[0., 15., 1.],
                            iterlim=200,
                            formats=["csv", "ndf"])

                ta = time.time()
                df = pd.read_csv("../foil_data/%s.csv" % foil_id)
                tb = time.time()
                logger.info("Pandas csv read took %f s" % (tb -ta))
                logger.info("%i records in csv file" % df.shape[0])
                df1 = df.dropna(how='any')
                logger.info("%i valid records in csv file" % df1.shape[0])

                df2 = pd.read_csv("../foil_data/%s.ndf" % foil_id,
                                  skiprows=1,
                                  delimiter=r"\s+")
                logger.info("%i records in ndf file" % df2.shape[0])
    else:
        raise EnvironmentError("Generating the data works better with Python 2")