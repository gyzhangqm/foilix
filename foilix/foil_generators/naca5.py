# coding: utf-8

r"""naca5series.py: Generates NACA 5 series airfoil.

For explanation of the equations used refer to:
http://web.stanford.edu/~cantwell/AA200_Course_Material/
                                               The%20NACA%20airfoil%20series.pdf

"""

from __future__ import print_function, division

import numpy as np
from parametric_foil import ParametricFoil


class NACA5(ParametricFoil):
    r"""NACA 5 series foil

    Parameters
    ----------
    mld :
        Mean line designation
    t : float
        Thickness in percentage of chord

    """
    def __init__(self, mld, t):
        self.mld = mld  # mean line designation
        self.t = t/100
        if mld == 210:
            self.m = .0580
            self.k1 = 361.40
            self.p = 0.05
        elif mld == 220:
            self.m = .1260
            self.k1 = 51.640
            self.p = 0.10
        elif mld == 230:
            self.m = .2025
            self.k1 = 15.957
            self.p = .15
        elif mld == 240:
            self.m = .2900
            self.k1 = 6.643
            self.p = 0.20
        elif mld == 250:
            self.m = .3910
            self.k1 = 3.23
            self.p = .25
        else:
            raise Warning("Unknown airfoil number. Try again.")
        # print self.m,self.k1,self.p

    def _fn_upper_lower(self, xpts):
        """Implements proper coordinate calculation, using camberline direction.

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
        dyc_dx[0] = (y_c[1]-y_c[0]) / (xpts[1] - xpts[0])
        dyc_dx[-1] = (y_c[-2]-y_c[-1]) / (xpts[-2] - xpts[-1])
        # Calculate camberline angle
        theta = np.arctan(dyc_dx)
        # Calculate x,y of upper, lower surfaces
        # From http://web.stanford.edu/~cantwell/AA200_Course_Material/
        # The%20NACA%20airfoil%20series.pdf
        x_u = xpts - y_t * np.sin(theta)
        y_u = y_c + y_t*np.cos(theta)
        x_l = xpts + y_t * np.sin(theta)
        y_l = y_c - y_t*np.cos(theta)
        return x_l, y_l, x_u, y_u, xpts, y_c

    def max_thickness(self):
        """Numerically compute max. thickness of airfoil"""
        # x_l, y_l, x_u, y_u = self.get_coords()[:4]
        _, y_l, _, y_u = self.get_coords()[:4]
        return max(y_u) - min(y_l)

    def _camberline(self, xpts):
        m, p = self.m, self.p
        k1 = self.k1
        if m == 0:
            return np.zeros(len(xpts))
        elif m != 0 and p == 0:
            raise Warning("Position of maximum camber is zero while the mean "
                          "camber is non-zero")
        else:
            xpts0 = xpts[xpts <= p]
            xpts1 = xpts[xpts > p]

            # from x=0 to x=p
            yc_0 = k1/6 * (xpts0**3 - 3*m*xpts0**2 + m**2 * (3-m)*xpts0)
            # from x=p to x=callable
            yc_1 = k1*m**3/6 * (1-xpts1)
            return np.append(yc_0, yc_1)

    def _thickness(self, xpts):
        t = self.t
        c = (.2969, .1260, .3516, .2843, .1015)
        y_t = t/.2 * (c[0] * xpts ** .5 - c[1] * xpts - c[2] * xpts ** 2 + c[3] * xpts ** 3 - c[4] * xpts ** 4)
        return y_t

    def __str__(self):
        return """NACA 5-series (pos. {}, thickness {})""".format(self.p,
                                                                  self.t)

    def is_symmetrical(self):
        r"""Check if the section is symmetrical

        Returns
        -------
        boolean : True for a symmetrical section, False for an
        asymetrical section

        """
        raise NotImplementedError
