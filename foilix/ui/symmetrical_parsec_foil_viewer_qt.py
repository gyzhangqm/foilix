#!/usr/bin/env python
# coding: utf-8

r"""symmetrical PARSEC visualization User Interface"""

from __future__ import division

import os
import sys

# Get rid of : Warning! ***HDF5 library version mismatched error***
os.environ['HDF5_DISABLE_VERSION_CHECK'] = "2"


try:
    from PySide import QtCore
    from PySide import QtGui
except ImportError:
    # pyqt comes by default with Anaconda
    from PyQt4 import QtCore
    from PyQt4 import QtGui
    QtCore.Signal = QtCore.pyqtSignal
    QtCore.Slot = QtCore.pyqtSlot
import pyqtgraph as pg  # not installed with default Anaconda install

from foilix.foil_generators.parsec import PARSEC

# Create the QApplication object
qt_app = QtGui.QApplication(sys.argv)


class LabelSliderValue(QtGui.QWidget):
    r"""Widget made of a label, a slider and a value.

    The label describes what the data is.
    The slider and the value represent the same value.

    The value can only be modified by the slider.

    Parameters
    ----------
    minimum : int
    maximum : int
    initial_value
    divider : int
    suffix : str

    """

    changed = QtCore.Signal(float)

    def __init__(self,
                 label,
                 minimum=0,
                 maximum=100,
                 initial_value=0,
                 divider=1,
                 suffix=''):
        QtGui.QWidget.__init__(self)

        self.divider = divider
        self.suffix = suffix

        layout = QtGui.QHBoxLayout(self)

        # label
        lbl = QtGui.QLabel(label, self)
        lbl.setMinimumWidth(140)
        lbl.setAlignment(QtCore.Qt.AlignRight)
        lbl.setAlignment(QtCore.Qt.AlignVCenter)

        # slider
        self.sl = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.sl.setFocusPolicy(QtCore.Qt.NoFocus)
        self.sl.setMaximum(maximum)
        self.sl.setMinimum(minimum)
        self.sl.setTickPosition(QtGui.QSlider.TicksBothSides)
        self.sl.setValue(initial_value)

        # value
        self.vl = QtGui.QLabel(self.string_value(), self)

        layout.addWidget(lbl)
        layout.addWidget(self.sl)
        layout.addWidget(self.vl)

        self.sl.valueChanged[int].connect(self.changeValue)

    def numeric_value(self):
        r"""Numeric value stored in the widget"""
        return self.sl.value() / self.divider

    def string_value(self):
        r"""String value of the value and suffix stored"""
        return "%s %s" % (str(self.numeric_value()), self.suffix)

    def changeValue(self, value):
        r"""What happens when the value changes

        Parameters
        ----------
        value : int

        """
        self.vl.setText(str(self.string_value()))
        self.changed.emit(self.numeric_value())


class ParsecFoilViewerApp(QtGui.QWidget):
    r"""A Qt application to visualize symmetrical PARSEC foil sections """
    def __init__(self):
        # Initialize the object as a QLabel
        QtGui.QWidget.__init__(self)

        # Set the size, alignment, and title
        self.setMinimumSize(QtCore.QSize(600, 400))
        self.setWindowTitle('Symmetrical PARSEC foil viewer')

        layout = QtGui.QVBoxLayout()

        self.thickness_lsv = LabelSliderValue('Thickness',
                                              maximum=1500,
                                              initial_value=600,
                                              divider=100,
                                              suffix='%')
        self.max_thickness_x_lsv = LabelSliderValue('Max Thickness X',
                                                    initial_value=250,
                                                    maximum=1000,
                                                    divider=10,
                                                    suffix='%')
        self.curvature_at_max_thickness_lsv = LabelSliderValue('Curvature at max thickness',
                                                               initial_value=25,
                                                               maximum=200,
                                                               minimum=-200,
                                                               divider=100)
        self.le_radius_lsv = LabelSliderValue('LE Radius',
                                              initial_value=50,
                                              maximum=200,
                                              divider=10000)
        self.te_angle_lsv = LabelSliderValue('TE Angle',
                                             initial_value=60,
                                             maximum=200,
                                             divider=10)

        self.button = QtGui.QPushButton('Toggle scale')

        k = {'rle': self.le_radius_lsv.numeric_value(),
             'x_pre': self.max_thickness_x_lsv.numeric_value() / 100,
             'y_pre': -self.thickness_lsv.numeric_value()/100./2.,
             'd2ydx2_pre': self.curvature_at_max_thickness_lsv.numeric_value(),
             'th_pre': self.te_angle_lsv.numeric_value(),
             'x_suc': self.max_thickness_x_lsv.numeric_value() / 100,
             'y_suc': self.thickness_lsv.numeric_value()/100./2.,
             'd2ydx2_suc': -self.curvature_at_max_thickness_lsv.numeric_value(),
             'th_suc': -self.te_angle_lsv.numeric_value(),
             'xte': 1.,
             'yte': 0.}

        self.pw = pg.PlotWidget()
        self.pw.setAspectLocked()
        self.locked = True

        self.plot_foil()

        layout.addWidget(self.thickness_lsv)
        layout.addWidget(self.max_thickness_x_lsv)
        layout.addWidget(self.curvature_at_max_thickness_lsv)
        layout.addWidget(self.le_radius_lsv)
        layout.addWidget(self.te_angle_lsv)
        layout.addWidget(self.pw)
        layout.addWidget(self.button)

        self.button.clicked.connect(self.toggle_scale)

        self.thickness_lsv.changed[float].connect(self.parameter_change)
        self.max_thickness_x_lsv.changed[float].connect(self.parameter_change)
        self.curvature_at_max_thickness_lsv.changed[float].connect(self.parameter_change)
        self.le_radius_lsv.changed[float].connect(self.parameter_change)
        self.te_angle_lsv.changed[float].connect(self.parameter_change)

        self.setLayout(layout)

    def foil_points(self):
        r"""Points describing the 2D foil section

        Returns
        -------
        ([x_lower],[y_lower],[x_upper],[y_upper])

        """
        k = {'rle': self.le_radius_lsv.numeric_value(),
             'x_pre': self.max_thickness_x_lsv.numeric_value() / 100,
             'y_pre': -self.thickness_lsv.numeric_value()/100./2.,
             'd2ydx2_pre': self.curvature_at_max_thickness_lsv.numeric_value(),
             'th_pre': self.te_angle_lsv.numeric_value(),
             'x_suc': self.max_thickness_x_lsv.numeric_value() / 100,
             'y_suc': self.thickness_lsv.numeric_value()/100./2.,
             'd2ydx2_suc': -self.curvature_at_max_thickness_lsv.numeric_value(),
             'th_suc': -self.te_angle_lsv.numeric_value(),
             'xte': 1.,
             'yte': 0.}

        return PARSEC(k).get_coords()

    def plot_foil(self):
        r"""Plot the foil"""
        self.pw.clear()
        pts = self.foil_points()
        self.pw.plot(x=pts[0], y=pts[1])
        self.pw.plot(x=pts[2], y=pts[3])

    def parameter_change(self, value):
        r"""What happens when a parameter changed"""
        self.plot_foil()

    @QtCore.Slot()
    def toggle_scale(self):
        r"""Toggle between real section shape and widened section shape"""
        if self.locked:
            self.locked = False
            self.pw.setAspectLocked(False)
        else:
            self.locked = True
            self.pw.setAspectLocked()
        self.plot_foil()

    def run(self):
        r"""Show the application window and start the main event loop"""
        self.show()
        qt_app.exec_()

# Create an instance of the application and run it
ParsecFoilViewerApp().run()
