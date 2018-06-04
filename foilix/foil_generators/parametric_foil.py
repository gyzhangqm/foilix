# coding: utf-8

r"""ParametricFoil abstract definition"""

from __future__ import division

from abc import ABCMeta, abstractmethod
import logging

import numpy as np
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


class ParametricFoil(object):
    r"""Base class for foil generators.

    The goal of this base class for foil generators is to share
    common functionality.

    When creating a child foil class, you have two choices:

    1. Define _fn_upper and _fn_lower methods, that calculate the coordinates
       of lower and upper surfaces, respectively.
    2. Define _camberline and _thickness, which calculate the coordinates
       of camberline and thickness, respectively.

    With the second method, ParametricFoil._fn_upper
                        and ParametricFoil._fn_lower are left to do their job,
    which is to nicely join the camberline and thickness, taking into account
    the camberline's direction,
    not simply summing camberline and thickness.

    Note
    ----
    Child classes should implement either:
    - _fn_upper_lower (_camberline and _thickness should
       raise NotImplementedError or call super method)
    - _camberline and _thickness (_fn_upper_lower should
      then call return super(NACA4, self)._fn_upper_lower(x))

    """
    __metaclass__ = ABCMeta

    # x coordinate of trailing edge, usually 1.0 for normalized foil
    # (Override if you know what you are doing).
    xte = 1.0

    @abstractmethod
    def is_symmetrical(self):
        r"""Check if the section is symmetrical

        Note
        ----
        This function has to be implemented in child classes

        """
        raise NotImplementedError

    @abstractmethod
    def _fn_upper_lower(self, xpts):
        r"""Implements proper coordinate calculation,
        using camberline direction"""
        raise NotImplementedError

    def max_thickness(self):
        r"""Compute maximum thickness of foil, taking camber into account

        Note
        ----
        This is the 'frontal' thickness of the foil. If the foil has no camber,
        the value should be the same as the nominal thickness.

        """
        # x_l, y_l, x_u, y_u = self.get_coords()[:4]
        _, y_l, _, y_u = self.get_coords()[:4]
        # return y_u.max() - y_l.min()
        return max(y_u) - min(y_l)

    def area(self):
        r"""Numerically compute volume of foil"""
        x_l, y_l, x_u, y_u = self.get_coords()[:4]
        # Use trapezoidal integration
        print(y_u)
        return np.trapz(y_u, x_u) - np.trapz(y_l, x_l)

    @abstractmethod
    def _camberline(self, xpts):
        raise NotImplementedError

    @abstractmethod
    def _thickness(self, xpts):
        raise NotImplementedError

    @abstractmethod
    def __str__(self):
        r"""Gives some information about the foil."""
        return "Foil object, implement __str__ method to give more info."

    def get_coords_plain(self, npts=161):
        r"""Returns string of coordinates in plain format."""
        # Ignore any camber line
        x_l, y_l, x_u, y_u = self.get_coords(npts=npts)[:4]
        # Evaluate and re-order to start at TE, over bottom, then top
        # Use slicing [1:] to remove [0,0]

        # ycoords = np.append(y_l[::-1], y_u[1:])
        # xcoords = np.append(x_l[::-1], x_u[1:])

        ycoords = np.append(y_u[::-1], y_l[1:])
        xcoords = np.append(x_u[::-1], x_l[1:])

        # Use .T to transpose to [[x,y],[x,y],...]
        coordslist = np.array((xcoords, ycoords)).T

        coordstrlist = ["{:.6f} {:.6f}".format(coord[0], coord[1])
                        for coord in coordslist]
        return '\n'.join(coordstrlist)  # Join with linebreaks in between

    def get_coords(self, npts=161):
        r"""Generates cosine-spaced coordinates, concentrated at LE and TE.

        Parameters
        ----------
        npts : positive integer, optional
            The number of coord points, default 161

        Returns
        -------
        ([x_lower],[y_lower],[x_upper],[y_upper])

        """
        xpts = (1 - np.cos(np.linspace(0, 1, np.ceil(npts / 2)) * np.pi)) / 2
        xpts *= self.xte  # Take TE position into account
        return self._fn_upper_lower(xpts)

    def plot(self, ax, score=None, title=None, style='r-'):
        r"""Plots foil outline given matplotlib.pyplot.Axes object

        Parameters
        ----------
        ax : matplotlib.pyplot.Axes object
            The axes object to display
        score : float, optional
            Score annotation
        title : string, optional
            Plot title
        style: string, optional
            Plot style

        """
        # ax.plot(x_l, y_l, style, x_u, y_u, style, linewidth=2)
        if len(self.get_coords()) == 4:
            x_l, y_l, x_u, y_u = self.get_coords()
        elif len(self.get_coords()) == 6:
            x_l, y_l, x_u, y_u, x_c, y_c = self.get_coords()
            ax.plot(x_c, y_c, "--", linewidth=1, color="grey", label="camber")
        else:
            logger.error("Unexpected number of coord lists")
            raise ValueError

        ax.plot(x_u, y_u, style, linewidth=2, color="red", label="upper")
        ax.plot(x_l, y_l, style, linewidth=2, color="orange", label="lower")

        if score:
            ax.annotate(str(score), (.4, 0))
        if title:
            ax.set_title(title)
        ax.legend()

    def plot_foil(self, title=None):
        r"""Matplotlib graph of foil shape including boilerplate code

        Parameters
        ----------
        title : str
            Plot title

        """
        fig = plt.figure()
        ax = fig.add_subplot(111)
        self.plot(ax, title=title)
        plt.gca().axis('equal')
        plt.show()
