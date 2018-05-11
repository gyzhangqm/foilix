#!/usr/bin/env python
# coding: utf-8

r"""wx based nurbs foil and dat foil file viewer"""

import os
import logging

import numpy as np

import wx
from wx.lib.agw.floatspin import FloatSpin
import wx.lib.agw.aui

import matplotlib
matplotlib.use('wx')

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar
import matplotlib.pyplot as plt

from atom.api import Atom, observe
from atom.dict import Dict
from atom.list import List
from atom.tuple import Tuple

from atom.scalars import Float

from foilix.foil_generators.nurbs import NURBS
from foilix.foil import Foil


class Model(Atom):
    r"""Data model for the viewer"""
    ref_foils = List(item=Foil)  # foilix.foil.Foil objects list

    ta = Float(default=0.1584)
    tb = Float(default=2.2)
    alpha = Float(default=12.)

    k = Dict()
    points = Tuple(item=np.ndarray)

    @observe("ta", "tb", "alpha")
    def nurbs_params_changed(self, change):
        r"""The nurbs definition parameters changed

        Parameters
        ----------
        change : dict

        """
        self.k = {'ta_u': self.ta,
                  'ta_l': self.ta,
                  'tb_u': self.tb,
                  'tb_l': self.tb,
                  'alpha_b': 2*self.alpha,
                  'alpha_c': -self.alpha}
        # self.points = NURBS(self.k).get_coords()
        # x_l, y_l, x_u, y_u = tuple(NURBS(self.k)._spline())
        # print(tuple(NURBS(self.k)._spline()))
        # self.points = (y_u, x_u, y_l, x_l)
        self.points = NURBS(self.k).get_coords()
        self.notify("nurbs_params_changed", change)

    def add_ref_foil(self, foil):
        r"""Add a reference foil

        Parameters
        ----------
        foil : foilix.foil.Foil
            A reference Foil object, created from a dat file in the UI

        """
        self.ref_foils.append(foil)
        self.notify("ref_foils_changed", None)


class LabelAndSpinner(wx.Panel):
    r"""Label and wx.lib.agw.floatspin.FloatSpin grouped in a wx.Panel

    Parameters
    ----------
    parent : wx.Window
        The parent window
    label : str
        The label
    initial_value : float
        The initial value of the FloatSpin
    minimum : float
        The minimum value of the FloatSpin
    maximum : float
        The maximum value of the FloatSPin
    digits : int
        The number of decimal digits of the FloatSpin
    increment : float
        The increment when the up/down arrows of the FloatSPin are pressed
    label_width : int
        The with of the label. Use for alignment purposes
    """

    def __init__(self,
                 parent,
                 label,
                 initial_value,
                 minimum,
                 maximum,
                 digits,
                 increment,
                 label_width):
        super(LabelAndSpinner, self).__init__(parent, wx.ID_ANY)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self,
                              wx.ID_ANY,
                              label,
                              size=(label_width, -1),
                              style=wx.ALIGN_RIGHT)
        self.spinner = FloatSpin(self,
                                 min_val=minimum,
                                 max_val=maximum,
                                 digits=digits,
                                 increment=increment,
                                 value=initial_value)
        sizer.Add(label, 0, wx.ALL, 5)
        sizer.Add(self.spinner, 0, wx.ALL, 5)
        self.SetSizer(sizer)


class GraphPanel(wx.Panel):
    r"""wx Panel embedding a Matplotlib plot

    Parameters
    ----------
    parent : wx parent
    model : Model
        The data model

    """
    # sequence of matplotlib included colors.
    # Used for the display of the reference foils
    color_sequence = ['dimgrey',
                      'maroon',
                      'darkolivegreen',
                      'darkred',
                      'tomato']
    nurbs_lower_color = 'orange'
    nurbs_upper_color = 'red'
    nurbs_lower_name = 'NURBS l'
    nurbs_upper_name = 'NURBS u'

    def __init__(self, parent, model):
        super(GraphPanel, self).__init__(parent, wx.ID_ANY)

        self.model = model
        #
        self.figure = plt.figure(facecolor='white')
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.canvas = FigureCanvas(self, -1, self.figure)

        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.Show()
        sizer.Add(self.canvas, 1, wx.EXPAND)
        sizer.Add(self.toolbar, 0)
        self.SetSizer(sizer)

        self.model.observe("nurbs_params_changed", self.on_model_changed)
        self.model.observe("ref_foils_changed", self.on_model_changed)
        self.on_model_changed(dict())

    def on_model_changed(self, change):
        r"""Handler for model changes, be it a parsec_params_changed or a
        ref_foils_changed change

        Parameters
        ----------
        change : dict
            Not used but must be present in function signature

        """
        colors = list()
        names = list()

        xs = list()
        ys = list()

        x_l, y_l, x_u, y_u = self.model.points[:4]
        xs.append(x_l)
        ys.append(y_l)
        colors.append(GraphPanel.nurbs_lower_color)
        names.append(GraphPanel.nurbs_lower_name)
        xs.append(x_u)
        ys.append(y_u)
        colors.append(GraphPanel.nurbs_upper_color)
        names.append(GraphPanel.nurbs_upper_name)

        for i, foil in enumerate(self.model.ref_foils):
            ref_foil_xs = [x for x, y in foil.points]
            ref_foil_ys = [y for x, y in foil.points]
            xs.append(ref_foil_xs)
            ys.append(ref_foil_ys)
            colors.append(GraphPanel.color_sequence[i % len(GraphPanel.color_sequence)])

            # ht* are the Drela foils.
            # Apart from ht22 and ht23, they are almost symmetrical
            if foil.is_symmetrical or 'ht' in foil.name:
                names.append("%s - th:%f -mx:%f - ler:%f" % (foil.name,
                                                             foil.y_spread,
                                                             foil.max_y_x,
                                                             foil.pseudo_leading_edge_radius))
            else:
                names.append(foil.name)

        self.plot(xs=xs, ys=ys, colors=colors, names=names)

    def plot(self, xs, ys, colors, names):
        r"""Plot values with an associated color and an associated name

        Parameters
        ----------
        xs : list of list of x values
        ys : list of list of y values, same order as xs
        colors : list of colors, same order as xs
        names : list of names, same order as xs

        """
        self.figure.clear()
        ax = self.figure.add_subplot(111, aspect='equal')
        plt.subplots_adjust(left=0.05, right=0.95, top=0.99, bottom=0.01)

        # can be hardcoded since x values of foil sections are bound to 0 -> 1
        ax.set_xlim(left=-.1, right=1.1)

        # can be hardcoded since y values of foils will never
        # exceed these bounds
        ax.set_ylim(bottom=-.25, top=.25)

        ax.set_yticks([-0.1, -0.08, -0.06, -0.04, -0.02, 0.,
                       0.02, 0.04, 0.06, 0.08, 0.1])
        ax.set_frame_on(False)  # outer frame
        #
        for x, y, color, name in reversed(list(zip(xs, ys, colors, names))):
            ax.plot(x, y, marker='+', color=color, label=name)

        ax.grid()

        legend = ax.legend(loc='upper left', shadow=True)
        if legend is not None:
            for label in legend.get_texts():
                label.set_fontsize('small')
            legend.draggable()

        self.canvas.draw()


class NurbsControlsPanel(wx.Panel):
    r"""Controls for the PARSEC foil"""
    def __init__(self, parent, model):
        super(NurbsControlsPanel, self).__init__(parent, wx.ID_ANY)
        self.model = model

        sizer = wx.BoxSizer(wx.VERTICAL)

        label_width = 100  # should be big enough to ensure proper alignment

        self.ta_widget = LabelAndSpinner(self,
                                         "ta",
                                         minimum=0.,
                                         maximum=10.,
                                         digits=10,
                                         increment=0.1,
                                         initial_value=self.model.ta,
                                         label_width=label_width)
        self.tb_widget = LabelAndSpinner(self,
                                         "tb",
                                         minimum=0.,
                                         maximum=10.,
                                         digits=10,
                                         increment=0.1,
                                         initial_value=self.model.tb,
                                         label_width=label_width)
        self.alpha_widget = LabelAndSpinner(self,
                                            "alpha",
                                            minimum=0.,
                                            maximum=10.,
                                            digits=10,
                                            increment=0.1,
                                            initial_value=self.model.alpha,
                                            label_width=label_width)

        sizer.Add(self.ta_widget)
        sizer.Add(self.tb_widget)
        sizer.Add(self.alpha_widget)

        self.SetSizer(sizer)

        # Bind the FloatSpins to a common callback
        self.ta_widget.spinner.Bind(wx.lib.agw.floatspin.EVT_FLOATSPIN,
                                    self.on_evt_floatspin,
                                    self.ta_widget.spinner)
        self.tb_widget.spinner.Bind(wx.lib.agw.floatspin.EVT_FLOATSPIN,
                                    self.on_evt_floatspin,
                                    self.tb_widget.spinner)
        self.alpha_widget.spinner.Bind(wx.lib.agw.floatspin.EVT_FLOATSPIN,
                                       self.on_evt_floatspin,
                                       self.alpha_widget.spinner)

        self.model.observe("nurbs_params_changed", self.on_nurbs_params_changed)

    def on_nurbs_params_changed(self, change):
        r"""Handler for a change in the values of the model nurbs parameters

        Parameters
        ----------
        change : dict
            Not used here. Present for function signature.

        """
        self.ta_widget.spinner.SetValue(self.model.ta)
        self.tb_widget.spinner.SetValue(self.model.tb)
        self.alpha_widget.spinner.SetValue(self.model.alpha)

    def on_evt_floatspin(self, event):
        r"""Handler for all the wx.lib.agw.floatspin.EVT_FLOATSPIN generated by
        the FloatSpins in self

        Parameters
        ----------
        event : wx event
            Not used. Present for function signature

        """
        self.model.ta = self.ta_widget.spinner.GetValue()
        self.model.tb = self.tb_widget.spinner.GetValue()
        self.model.alpha = self.alpha_widget.spinner.GetValue()


class NurbsFoilViewerFrame(wx.Frame):
    r"""Main frame of the application

    Parameters
    ----------
    model : Model
    title : str
        Frame title
    save_on_close : str or None
        If None, do nothing. If valid file path, save the parameters values
    """
    def __init__(self,
                 model,
                 title="Symmetrical NURBS Foil Viewer",
                 save_on_close=None):
        super(NurbsFoilViewerFrame, self).__init__(None,
                                                   wx.ID_ANY,
                                                   title=title,
                                                   size=(600, 400))
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.model = model
        self.save_on_close = save_on_close

        menubar = wx.MenuBar()

        # File menu
        file_menu = wx.Menu()
        self.add_menu_item(menu=file_menu,
                           wx_id=wx.ID_NEW,
                           text='&Load dat file\tCtrl+L',
                           handler=self.on_load)
        menubar.Append(file_menu, '&File')

        self.SetMenuBar(menubar)

        self.controls_panel = NurbsControlsPanel(self, self.model)
        self.graph_panel = GraphPanel(self, self.model)
        #
        self._mgr = wx.lib.agw.aui.AuiManager()
        self._mgr.SetManagedWindow(self)
        self._mgr.AddPane(self.controls_panel, wx.lib.agw.aui.AuiPaneInfo().
                          Right().Name("Controls").Caption("Controls").
                          MinSize(wx.Size(200, 200)).MaximizeButton(True))
        self._mgr.AddPane(self.graph_panel,
                          wx.lib.agw.aui.AuiPaneInfo().CenterPane())
        self._mgr.Update()

        self.CenterOnScreen()
        self.Maximize(True)

    def on_load(self, event):
        r"""Handler of the File > Load dat file menu item

        Parameters
        ----------
        event : wx event
            Not used here. Present for function signature.

        """
        dat_file_dialog = wx.FileDialog(self,
                                        message="Choose a file",
                                        defaultFile="",
                                        defaultDir=os.environ["FOIL_DATA_FOLDER"],
                                        wildcard="DAT files (*.dat)|*.dat",
                                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_CHANGE_DIR)
        if dat_file_dialog.ShowModal() == wx.ID_OK:
            path = dat_file_dialog.GetPath()

            foil = Foil.from_dat_file(path)
            self.model.add_ref_foil(foil)
        dat_file_dialog.Destroy()

    def add_menu_item(self,
                      menu,
                      wx_id,
                      text,
                      handler,
                      icon=None,
                      enabled=True):
        r"""Add an item to a menu

        Parameters
        ----------
        menu : wx.Menu
        wx_id : int
        text : str
            Menu test
        handler : function
        icon : str
            Path to the icon file
        enabled : bool

        """
        menu_item = wx.MenuItem(parentMenu=menu, id=wx_id, text=text)
        if icon is not None:
            menu_item.SetBitmap(wx.Bitmap(icon))
        menu.Append(menu_item)
        if enabled is True:
            self.Bind(event=wx.EVT_MENU, handler=handler, id=wx_id)
        else:
            menu_item.Enable(False)

    def on_close(self, event):
        r"""Handle a click on the closing button (upper right cross)
        of the frame

        Parameters
        ----------
        event : wx.event

        """
        dlg = wx.MessageDialog(self,
                               "Do you really want to close this application?",
                               "Confirm Exit",
                               wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            if self.save_on_close is not None:
                with open(self.save_on_close, 'w') as f:
                    f.write("ta,%s" % str(self.controls_panel.ta_widget.spinner.GetValue()) + "\n")
                    f.write("tb,%s" % str(self.controls_panel.tb_widget.spinner.GetValue()) + "\n")
                    f.write("alpha,%s" % str(self.controls_panel.alpha_widget.spinner.GetValue()) + "\n")
            self.Destroy()
        # self.Destroy()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s :: %(levelname)6s :: %(module)20s '
                               ':: %(lineno)3d :: %(message)s')

    app = wx.App()
    model_ = Model()
    frame = NurbsFoilViewerFrame(model_)
    frame.Show(True)
    app.SetTopWindow(frame)
    app.MainLoop()
