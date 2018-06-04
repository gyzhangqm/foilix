# coding: utf-8

r"""NACA 4 digit generator"""

from __future__ import print_function, division

import numpy as np

from foilix.foil_generators.parametric_foil import ParametricFoil


class NACA4(ParametricFoil):
    r"""NACA 4 series foil generator.

    Parameters
    ----------
    max_camber : float
        maximum camber in hundredths of chord
    max_camber_position : float
        position of max. camber in tenths of chord.
    thickness : float
        thickness in percent.

    References
    ----------
    For an explanation on equations used, see NASA Technical Memorandum 4741
    Short explanation: http://web.stanford.edu/~cantwell/
                            AA200_Course_Material/The%20NACA%20foil%20series.pdf

    Doctests
    --------
    >>> foil = NACA4(max_camber=8, max_camber_position=4, thickness=15)
    >>> print(foil)
    NACA 4-series (camber 0.08, pos. 0.4, thickness 0.15)
    >>> print("Real thickness (including camber): {:.1%}".format(foil.max_thickness()))
    Real thickness (including camber): 17.7%
    >>> print("Volume: {:.3f} chord^2".format(foil.area()))
    Volume: 0.104 chord^2
    >>> foil = NACA4(max_camber=0, max_camber_position=0, thickness=15)
    >>> print(foil)
    NACA 4-series (camber 0.0, pos. 0.0, thickness 0.15)
    >>> print("Real thickness (including camber): {:.1%}".format(foil.max_thickness()))
    Real thickness (including camber): 15.0%
    >>> print("Volume: {:.3f} chord^2".format(foil.area()))
    Volume: 0.103 chord^2

    """

    def __init__(self, max_camber, max_camber_position, thickness):
        # max camber beyond 50 % is unrealistic
        if max_camber < 0 or max_camber > 50:
            raise ValueError("Maximum camber should be between 0 and 50")
        if max_camber_position < 0 or max_camber_position >= 10:
            raise ValueError("Maximum camber position should be between "
                             "0 and 10")
        # thickness beyond 50 % is unrealistic
        if thickness < 0 or thickness > 50:
            raise ValueError("Thickness should be between 0 and 50")

        self.max_camber = max_camber / 100
        self.max_camber_position = max_camber_position / 10
        self.thickness = thickness / 100

    def is_symmetrical(self):
        r"""Check if the section is symmetrical

        Returns
        -------
        boolean : True for a symmetrical section, False for an
        assymetrical section

        """
        if self.max_camber == 0:
            return True
        else:
            return False

    def _fn_upper_lower(self, xpts):
        r"""Implements proper coordinate calculation, using camberline direction

        Parameter
        ----------
        x : 1D numpy.ndarray of floats
            An 1-dimensional array containing samples of x coordinates.

        Returns
        -------
        (x_upper, y_upper, x_lower, y_lower, x_camber, y_camber)

        """
        y_t = self._thickness(xpts)
        y_c = self._camberline(xpts)

        # Calculate camber line derivative using central difference
        dx = np.gradient(xpts)

        # Numpy 1.12 induced bug correction
        # dyc_dx = np.gradient(y_c, dx)
        dyc_dx = np.gradient(y_c) / dx

        # np.gradient calculates the edges weirdly, replace them by fwd diff
        # Can be made even more accurate by using second-order fwd diff,
        # but that is not so straightforward when step size differs.
        # Numpy 1.9.1 supports edge_order=2 in np.gradient()
        dyc_dx[0] = (y_c[1] - y_c[0]) / (xpts[1] - xpts[0])
        dyc_dx[-1] = (y_c[-2] - y_c[-1]) / (xpts[-2] - xpts[-1])

        # Calculate camberline angle
        theta = np.arctan(dyc_dx)

        # Calculate x,y of upper, lower surfaces
        # From http://web.stanford.edu/~cantwell/AA200_Course_Material/
        #                                      The%20NACA%20airfoil%20series.pdf
        x_l = xpts - y_t * np.sin(theta)

        # reverse sign for coherence with parsec
        y_l = (y_c + y_t * np.cos(theta))

        x_u = xpts + y_t * np.sin(theta)

        # reverse sign for coherence with parsec
        y_u = (y_c - y_t * np.cos(theta))

        return x_u, y_u, x_l, y_l, xpts, y_c

    def _camberline(self, xpts):
        max_camber, max_camber_position = \
            self.max_camber, self.max_camber_position
        if max_camber == 0:
            return np.zeros(len(xpts))
        elif max_camber != 0 and max_camber_position == 0:
            raise Warning("Position of max camber is zero while "
                          "camber is nonzero.")
        else:
            xpts0 = xpts[xpts <= max_camber_position]
            xpts1 = xpts[xpts > max_camber_position]
            # From x=0 to x=max_camber_position
            y_c0 = (max_camber/max_camber_position**2 *
                    (2 * max_camber_position * xpts0 - xpts0**2))
            # From x=p to x=c
            y_c1 = (max_camber / (1 - max_camber_position)**2 *
                    ((1 - 2 * max_camber_position) + 2 *
                     max_camber_position * xpts1 - xpts1**2))
            return np.append(y_c0, y_c1)

    def _thickness(self, xpts):
        r"""Computes the thicknesses at the input locations

        Parameters
        ----------
        xpts : 1D numpy/ndarray of floats
            Locations along the chord (usually between 0 and 1)

        Returns
        -------
        y_t : 1D numpy.ndarray of floats
            Thicknesses at the given locations
        """
        thickness = self.thickness
        c = (.2969, .1260, .3516, .2843, .1015)
        y_t = thickness / .2 * (c[0] * xpts ** .5
                                - c[1] * xpts
                                - c[2] * xpts ** 2
                                + c[3] * xpts ** 3
                                - c[4] * xpts ** 4)
        return y_t

    def __str__(self):
        r"""String representation of NACA4 foil"""
        return "NACA 4-series (camber {}, pos. {}, " \
               "thickness {})".format(self.max_camber,
                                      self.max_camber_position,
                                      self.thickness)
