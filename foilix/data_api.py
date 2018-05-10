# coding: utf-8

import logging

from os.path import join

import pandas as pd

from corelib.core.memoize import memoize
from corelib.core.profiling import timeit
from corelib.core.files import p_

from libra.data_model_import import create_partial_data_model_from_file


foil_data_folder = p_(__file__, "../foil_data")


def foil_file_summary_csv(foil_id):
    return data_file_summary_csv(join(foil_data_folder, "%s.csv" % foil_id))


def foil_file_summary_ndf(foil_id):
    return data_file_summary_ndf(join(foil_data_folder, "%s.ndf" % foil_id))


def data_file_summary_csv(csv_file_path):
    df = pd.read_csv(csv_file_path)
    ranges = {'mach': (df['mach'].min(), df['mach'].max()),
              'ncrit': (df['ncrit'].min(), df['ncrit'].max()),
              'reynolds': (df['reynolds'].min(), df['reynolds'].max()),
              'aoa': (df['aoa'].min(), df['aoa'].max())}
    return df.shape[0], df.dropna(how='any').shape[0], ranges


def data_file_summary_ndf(ndf_file_path):
    df = pd.read_csv(ndf_file_path, skiprows=1, delimiter=r"\s+")
    pm = create_interpolation_model(ndf_file_path)
    return df.shape[0], df.dropna(how='any').shape[0], pm.input_continuous_ranges


@memoize
@timeit
def create_interpolation_model(ndf_file_path):
    pm = create_partial_data_model_from_file(ndf_file_path)
    # print(pm.input_continuous_ranges)
    return pm


@timeit
def get_data_dict(foil_id, mach, ncrit, reynolds, aoa):
    pm = create_interpolation_model(join(foil_data_folder, "%s.ndf" % foil_id))
    ir = pm.input_continuous_ranges

    if not (ir['mach'][0] <= mach <= ir['mach'][1]):
        raise ValueError("mach (%.2f) outside of data model range "
                         "(%.2f to %.2f)" % (mach,
                                             ir['mach'][0],
                                             ir['mach'][1]))
    if not (ir['ncrit'][0] <= ncrit <= ir['ncrit'][1]):
        raise ValueError("ncrit (%.2f) outside of data model range "
                         "(%.2f to %.2f)" % (ncrit,
                                             ir['ncrit'][0],
                                             ir['ncrit'][1]))
    if not (ir['reynolds'][0] <= reynolds <= ir['reynolds'][1]):
        raise ValueError("reynolds (%.2f) outside of data model range "
                         "(%.2f to %.2f)" % (reynolds,
                                             ir['reynolds'][0],
                                             ir['reynolds'][1]))
    if not (ir['aoa'][0] <= aoa <= ir['aoa'][1]):
        raise ValueError("aoa (%.2f) outside of data model range "
                         "(%.2f to %.2f)" % (aoa, ir['aoa'][0], ir['aoa'][1]))

    r_initial = pm.interpolate({'mach': mach,
                                'ncrit': ncrit,
                                'reynolds': reynolds,
                                'aoa': aoa})

    r = {}
    for k, v in r_initial.items():
        r[k] = float(v)

    return r


def get_data_tuple(foil_id, mach, ncrit, reynolds, aoa):
    r = get_data_dict(foil_id, mach, ncrit, reynolds, aoa)
    return r['cl'], r['cd'], r['cdp'], r['cm'], r['top_xtr'], r['bot_xtr']

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s :: %(levelname)6s :: %(module)20s '
                               ':: %(lineno)3d :: %(message)s')
    print(get_data_dict("naca0006", mach=0.0, ncrit=1.0, reynolds=5e4, aoa=1.0))
    print(get_data_tuple("naca0006", mach=0.0, ncrit=1.0, reynolds=5e4, aoa=2.0))
    print(
        get_data_tuple("naca0006", mach=0.0, ncrit=4.0, reynolds=5e4, aoa=15.0))
    print(60 * "*")
    print(foil_file_summary_csv("naca0006"))
    print(foil_file_summary_ndf("naca0006"))
