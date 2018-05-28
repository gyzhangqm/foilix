#!/usr/bin/env python
# coding: utf-8

r"""PSO UI monitoring tool"""

from __future__ import division

import sys

import wx
from wx.lib.agw import ultimatelistctrl as ULC

from foilix.ui.observer import Observer


class LoggingFrame(wx.Frame, Observer):
    r"""Frame that receives info to display via its update() method

    Designed to display information from a pso optimization,
    to monitor what is going on

    """
    def __init__(self, parent=None, title="Logging Frame"):
        wx.Frame.__init__(self, parent, wx.NewId(), title)
        self.log_window = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE)
        self.log_window.Show()
        self.Bind(wx.EVT_CLOSE, self._on_close)

    def update(self, message, n, i_par, pts, score):
        r"""

        Parameters
        ----------
        message : str
            Message prefix
        n : int
        i_par : int
        pts : str
            String representation of a pso position
        score : float

        """
        message = "%s - %i - %i - %s - %f" % (message,
                                              n,
                                              i_par,
                                              str(pts),
                                              1./score)
        self.log_window.AppendText(message + "\n")
        # wx.CallAfter(self.add_text, message)

    def _on_close(self, event):
        self.log_window.this.disown()
        wx.Log.SetActiveTarget(None)
        event.Skip()


class NewLoggingFrame(wx.Frame, Observer):
    r"""Frame that receives info to display via its update() method

    Designed to display information from a pso optimization,
    to monitor what is going on

    """
    def __init__(self, parent=None, title="Logging Frame"):
        super(NewLoggingFrame, self).__init__(parent,
                                              wx.NewId(),
                                              title,
                                              size=(1200, -1))
        # wx.Frame.__init__(self, parent, wx.NewId(), title, size=(1000, -1))

        self.nb_records = 0

        self.ultimate_list = ULC.UltimateListCtrl(self,
                                                  agwStyle=wx.LC_REPORT | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT)

        info = ULC.UltimateListItem()
        info._mask = wx.LIST_MASK_TEXT
        info._text = "Message"
        self.ultimate_list.InsertColumnInfo(0, info)

        info = ULC.UltimateListItem()
        info._mask = wx.LIST_MASK_TEXT
        info._text = "n"
        self.ultimate_list.InsertColumnInfo(1, info)

        info = ULC.UltimateListItem()
        info._mask = wx.LIST_MASK_TEXT
        info._text = "I par"
        self.ultimate_list.InsertColumnInfo(2, info)

        info = ULC.UltimateListItem()
        info._mask = wx.LIST_MASK_TEXT
        info._text = "Pts"
        self.ultimate_list.InsertColumnInfo(3, info)

        info = ULC.UltimateListItem()
        info._mask = wx.LIST_MASK_TEXT
        info._text = "Score"
        self.ultimate_list.InsertColumnInfo(4, info)

        info = ULC.UltimateListItem()
        info._mask = wx.LIST_MASK_TEXT
        info._text = "Inv Score"
        self.ultimate_list.InsertColumnInfo(5, info)

        info = ULC.UltimateListItem()
        info._mask = wx.LIST_MASK_TEXT
        info._text = "Thickness"
        self.ultimate_list.InsertColumnInfo(6, info)

        info = ULC.UltimateListItem()
        info._mask = wx.LIST_MASK_TEXT
        info._text = "Max Th X"
        self.ultimate_list.InsertColumnInfo(7, info)

        self.ultimate_list.SetColumnWidth(0, 150)
        self.ultimate_list.SetColumnWidth(1, 40)
        self.ultimate_list.SetColumnWidth(2, 40)
        self.ultimate_list.SetColumnWidth(3, 500)
        self.ultimate_list.SetColumnWidth(4, 100)
        self.ultimate_list.SetColumnWidth(5, 100)
        self.ultimate_list.SetColumnWidth(6, 100)
        self.ultimate_list.SetColumnWidth(7, 100)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.ultimate_list, 1, wx.EXPAND)
        self.SetSizer(sizer)

        # self.log_window.Show()
        self.Bind(wx.EVT_CLOSE, self._on_close)

    def update(self, message, n, i_par, pts, score, parameterization_type):
        r"""

        Parameters
        ----------
        message : str
            Message prefix
        n : int
        i_par : int
        pts : str
            String representation of a pso position
        score : float
        parameterization_type : str

        """
        item = self.ultimate_list.InsertStringItem(self.nb_records, message)
        if message == "global_best":
            self.ultimate_list.SetItemBackgroundColour(item,
                                                       wx.Colour(255, 100, 220))
        elif message == "particle_best":
            self.ultimate_list.SetItemBackgroundColour(item,
                                                       wx.Colour(240, 240, 240))

        self.ultimate_list.SetStringItem(self.nb_records, 1, str(n))
        self.ultimate_list.SetStringItem(self.nb_records, 2, str(i_par))
        self.ultimate_list.SetStringItem(self.nb_records, 3, str(pts))
        self.ultimate_list.SetStringItem(self.nb_records, 4, str(score))
        self.ultimate_list.SetStringItem(self.nb_records, 5, str(1/score))

        if parameterization_type == "SYM_PARSEC":
            from foilix.foil_generators.parsec import PARSEC
            k = dict()
            k['rle'] = pts[1]
            k['x_pre'] = pts[2]
            # Thickness 6%
            k['y_pre'] = -pts[0] / 2.0
            k['d2ydx2_pre'] = -pts[3]
            # Trailing edge angle
            k['th_pre'] = pts[4]
            # Suction part
            k['x_suc'] = k['x_pre']
            k['y_suc'] = -k['y_pre']
            k['d2ydx2_suc'] = -k['d2ydx2_pre']
            k['th_suc'] = -k['th_pre']
            # Trailing edge x and y position
            k['xte'] = 1.0  # beware of PARSEC generator check
            k['yte'] = 0.0
            foil = PARSEC(k)
            self.ultimate_list.SetStringItem(self.nb_records,
                                             6,
                                             str(foil.max_thickness()))
            self.ultimate_list.SetStringItem(self.nb_records,
                                             7,
                                             str(k['x_pre']))
        elif parameterization_type == "SYM_NURBS":
            from foilix.foil_generators.nurbs import NURBS
            ta = pts[0]
            tb = pts[1]
            alpha = pts[2]
            k = {'ta_u': ta,
                 'ta_l': ta,
                 'tb_u': tb,
                 'tb_l': tb,
                 'alpha_b': 2*alpha,
                 'alpha_c': -alpha}
            foil = NURBS(k)
            self.ultimate_list.SetStringItem(self.nb_records,
                                             6,
                                             str(foil.max_thickness()))
            x_l, y_l, x_u, y_u, = foil.get_coords()
            self.ultimate_list.SetStringItem(self.nb_records,
                                             7,
                                             str(x_u[y_u.tolist().index(max(y_u))]))
        elif parameterization_type == "NURBS" \
                or parameterization_type == "SYM_PARSEC":
            raise NotImplementedError

        self.nb_records += 1

    def _on_close(self, event):
        # self.ultimate_list.this.disown()
        wx.Log.SetActiveTarget(None)
        event.Skip()
        self.Destroy()
        sys.exit(0)


if __name__ == "__main__":
    app = wx.App()
    logging_frame = NewLoggingFrame()
    logging_frame.Show()
    app.MainLoop()
