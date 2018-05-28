#!/usr/bin/env python
# coding: utf-8

r"""Step 2 of the optimization procedure :
- find the parameters of a nurbs foil that are close to the best foils
  from the database
- the parameters are saved (to the 'save_on_close' parameter of the 
  NurbsFoilViewerFrame constructor) when the viewer is closed

"""

from os import getcwd
from os.path import join
import logging
from argparse import ArgumentParser

import wx

from foilix.read_config import read_config

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s :: %(levelname)6s :: %(module)20s :: '
                           '%(lineno)3d :: %(message)s')

logger = logging.getLogger(__name__)

config = read_config(join(getcwd(), "foilix_case.conf"))


def nurbs():

    from foilix.ui.symmetrical_nurbs_foil_viewer_wx import NurbsFoilViewerFrame, \
        Model

    initial_nurbs_foil_params_filename = join(getcwd(),
                                              "initial_nurbs_foil_params.data")

    app = wx.App()
    model_ = Model()

    frame = NurbsFoilViewerFrame(model_,
                                 save_on_close=initial_nurbs_foil_params_filename,
                                 default_dat_folder=config["foil_dat_folder"])

    frame.Show(True)
    app.SetTopWindow(frame)
    app.MainLoop()
    logger.info("Parsec parameters written to %s" %
                initial_nurbs_foil_params_filename)


def parsec():

    from foilix.ui.symmetrical_parsec_foil_viewer_wx import \
        ParsecFoilViewerFrame, Model

    initial_parsec_foil_params_filename = join(getcwd(),
                                               "initial_parsec_foil_params.data")

    app = wx.App()
    model_ = Model()

    frame = ParsecFoilViewerFrame(model_,
                                  save_on_close=initial_parsec_foil_params_filename,
                                  default_dat_folder=config["foil_dat_folder"])

    frame.Show(True)
    app.SetTopWindow(frame)
    app.MainLoop()
    logger.info("Parsec parameters written to %s" %
                initial_parsec_foil_params_filename)


def main():
    parser = ArgumentParser(description="Foilix Opt step 2")
    parser.add_argument('-n', '--nurbs',
                        action='store_true',
                        help="Use NURBS parameterization")
    parser.add_argument('-p', '--parsec',
                        action='store_true',
                        help="Use PARSEC parameterization")
    args = parser.parse_args()
    if args.nurbs is True:
        if args.parsec is True:
            raise ValueError("Specify a single parameterization to use")
        else:
            nurbs()
    else:
        if args.parsec is True:
            parsec()
        else:
            raise ValueError("Specify which parameterization to use")


if __name__ == "__main__":
    main()
