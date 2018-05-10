#!/usr/bin/env python
# coding: utf-8

r"""Step 2 of the optimization procedure :
- find the parameters of a parsec foil that are close to the best foils
from the database
- the parameters are saved (to the 'save_on_close' parameter of the
ParsecFoilViewerFrame constructor)
 when the viewer is closed
"""

import logging

import wx

from foilix.ui.symmetrical_parsec_foil_viewer_wx import ParsecFoilViewerFrame, Model
import optimization_procedure_step0_define_problem as op_def


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s :: %(levelname)6s :: %(module)20s :: '
                           '%(lineno)3d :: %(message)s')

logger = logging.getLogger(__name__)

app = wx.App()
model_ = Model()

# initial_foil_file = join(dirname(__file__), "initial_parsec_foil_params.data")
frame = ParsecFoilViewerFrame(model_,
                              save_on_close=op_def.initial_parsec_foil_params_filename)

frame.Show(True)
app.SetTopWindow(frame)
app.MainLoop()
logger.info("Parsec parameters written to %s" % 
            op_def.initial_parsec_foil_params_filename)