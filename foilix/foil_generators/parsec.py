# coding: utf-8

r"""PARSEC foil generator"""

from __future__ import division, print_function

from itertools import groupby

import numpy as np

import foilix.foil_generators.parametric_foil


class PARSEC(foilix.foil_generators.parametric_foil.ParametricFoil):
    r"""PARSEC parametric foil generator.

    See also
    --------
    foilix/ui/symmetrical_parsec_foil_viewer.py

    References
    ----------
    http://www.as.dlr.de/hs/d.PARSEC/Parsec.html
    http://www.as.dlr.de/hs/h-pdf/H141.pdf
    http://github.com/dqsis/parsec-airfoils

    Doctests
    --------
    # Symmetrical foil section
    >>> x = 0.25
    >>> y = 0.03
    >>> d2ydx2 = 0.25
    >>> th = 6.
    >>> k = {'rle': .005,'x_pre': x, 'y_pre': -y, 'd2ydx2_pre': d2ydx2, 'th_pre': th, 'x_suc': x, 'y_suc': y, 'd2ydx2_suc': -d2ydx2, 'th_suc': -th, 'xte': 1., 'yte': 0.}
    >>> foil = PARSEC(k)
    >>> print(foil)
    Airfoil with PARSEC parametrization. Coefficients: 
    {'y_pre': -0.03,
    'x_suc': 0.25,
    'x_pre': 0.25,
    'rle': 0.005,
    'y_suc': 0.03,
    'd2ydx2_pre': 0.25,
    'th_pre': 6.0,
    'd2ydx2_suc': -0.25,
    'xte': 1.0,
    'th_suc': -6.0,
    'yte': 0.0}
    >>> foil.is_symmetrical()
    True
    >>> foil.is_valid()
    True
    """

    def __init__(self, k):
        r"""Takes a dict of coefficients to define PARSEC foil.

        Parameters
        ----------
        k : dict
            Dictionary of coefficients

            Coefficient names:
            rle:        leading edge radius
            xte:        x position of trailing edge
            yte:        y position of trailing edge
            x_suc:      suction surface crest location x
            y_suc:      suction surface crest location y
            d2ydx2_suc: curvature at the suction surface crest location
            th_suc:     trailing edge angles between the suction surface 
                        and the horizontal axis
            x_pre:      pressure surface crest location x
            y_pre:      pressure surface crest location y
            d2ydx2_pre: curvature at the pressure surface crest location
            th_pre:     trailing edge angles between the pressure surface
                        and the horizontal axis

        """
        if k['rle'] <= 0.0 or k['rle'] >= 1.0:
            raise ValueError("Leading edge radius should be between 0 and 1")
        if k['xte'] != 1.0:
            raise ValueError("Foil should be normalized")
        if k['yte'] < -0.1 or k['yte'] > 0.1:
            raise ValueError("Unrealistic trailing edge y")
        if k['x_suc'] < 0.0 or k['x_suc'] > 1.0:
            raise ValueError("Unrealistic suction surface crest location x")
        if k['y_suc'] < 0.0 or k['y_suc'] > 0.5:
            raise ValueError("Unrealistic suction surface crest location x")
        if k['d2ydx2_suc'] < -2.0 or k['d2ydx2_suc'] > 2.0:
            raise ValueError("Unrealistic curvature at the suction surface "
                             "crest location")
        if k['th_suc'] < -40.0 or k['th_suc'] > 0.0:
            raise ValueError("Unrealistic curvature at the suction surface "
                             "crest location")
        if k['x_pre'] < 0.0 or k['x_pre'] > 1.0:
            raise ValueError("Unrealistic suction surface crest location x")
        if k['y_pre'] < -0.5 or k['y_pre'] > 0.0:
            raise ValueError("Unrealistic pressure surface crest location x")
        if k['d2ydx2_pre'] < -2.0 or k['d2ydx2_pre'] > 2.0:
            raise ValueError("Unrealistic curvature at the pressure surface "
                             "crest location")
        if k['th_pre'] < 0.0 or k['th_pre'] > 40.0:
            raise ValueError("Unrealistic curvature at the pressure surface "
                             "crest location")

        self.k = k
        try:
            # Parent class contains functions that need to know x-pos of TE
            self.xte = k['xte']
    
            self.coeffs_upper = self._pcoef(k['xte'],
                                            k['yte'],
                                            k['rle'],
                                            k['x_suc'],
                                            k['y_suc'],
                                            k['d2ydx2_suc'],
                                            k['th_suc'],
                                            'suction')
            self.coeffs_lower = self._pcoef(k['xte'],
                                            k['yte'],
                                            k['rle'],
                                            k['x_pre'],
                                            k['y_pre'],
                                            k['d2ydx2_pre'],
                                            k['th_pre'],
                                            'pressure')
        except TypeError:
            raise Warning("Pass a dict with named coefficients.\n" +
                          "Explanation:\n" + self.__init__.__doc__)
        except KeyError as e:
            raise Warning("{:s} was not defined in the dict".format(e))

    def __str__(self):
        """Gives some information on foil"""
        return "Airfoil with PARSEC parametrization. " \
               "Coefficients: {}".format(self.k)

    def _fn_upper_lower(self, xpts):
        r"""

        This is the implementation of the abstract method of ParametricFoil

        Parameters
        ----------
        xpts

        Returns
        -------

        """
        # return (xpts,
        #         self._calc_coords(xpts, self.coeffs_upper),
        #         xpts,
        #         self._calc_coords(xpts, self.coeffs_lower))
        return (xpts,
                self._calc_coords(xpts, self.coeffs_lower),
                xpts,
                self._calc_coords(xpts, self.coeffs_upper))

    def _camberline(self, xpts):
        raise NotImplementedError

    def _thickness(self, xpts):
        raise NotImplementedError

    @staticmethod
    def _calc_coords(xpts, coeffs):
        # Powers to raise coefficients to. from __future___ import division!
        pwrs = (1/2, 3/2, 5/2, 7/2, 9/2, 11/2)

        # Make [[1,1,1,1],[2,2,2,2],...] style array
        xptsgrid = np.meshgrid(np.arange(len(pwrs)), xpts)[1]

        # Evaluate points with concise matrix calculations.
        # One x-coordinate is evaluated for every row in xptsgrid
        return np.sum(coeffs * xptsgrid**pwrs, axis=1)

    @staticmethod
    def _pcoef(xte, yte, rle, x_cre, y_cre, d2ydx2_cre, th_cre, surface):
        r"""Evaluate the PARSEC coefficients.

        Reference
        ---------
        From https://github.com/dqsis/parsec-airfoils

        """
        # Initialize coefficients
        coef = np.zeros(6)

        # 1st coefficient depends on surface (pressure or suction)
        if surface == 'pressure':
            coef[0] = -np.sqrt(2*rle)
        elif surface == 'suction':
            coef[0] = np.sqrt(2*rle)

        # Form system of equations
        A = np.array([
                      [xte**1.5, xte**2.5, xte**3.5, xte**4.5, xte**5.5],
                      [x_cre**1.5,
                       x_cre**2.5,
                       x_cre**3.5,
                       x_cre**4.5,
                       x_cre**5.5],
                      [1.5 * np.sqrt(xte),
                       2.5 * xte**1.5,
                       3.5 * xte**2.5,
                       4.5 * xte**3.5,
                       5.5 * xte**4.5],
                      [1.5 * np.sqrt(x_cre),
                       2.5 * x_cre**1.5,
                       3.5 * x_cre**2.5,
                       4.5 * x_cre**3.5,
                       5.5 * x_cre**4.5],
                      [0.75 * (1 / np.sqrt(x_cre)),
                       3.75 * np.sqrt(x_cre),
                       8.75 * x_cre**1.5,
                       15.75 * x_cre**2.5,
                       24.75 * x_cre**3.5]
                     ])
        B = np.array([
                      [yte - coef[0] * np.sqrt(xte)],
                      [y_cre - coef[0] * np.sqrt(x_cre)],
                      [np.tan(th_cre * np.pi/180) - 0.5 * coef[0] *
                       (1 / np.sqrt(xte))],
                      [-0.5 * coef[0] * (1 / np.sqrt(x_cre))],
                      [d2ydx2_cre + 0.25 * coef[0] * x_cre**(-1.5)]
                     ])

        X = np.linalg.solve(A, B)  # Solve system of linear equations
        coef[1:6] = X[0:5, 0]  # Gather all coefficients
        return coef  # Return coefficients

    def is_symmetrical(self):
        r"""Check if the section is symmetrical.

        This is the implementation of the abstract method of ParametricFoil

        Returns
        -------
        boolean : True for a symmetrical section,
                  False for an assymetrical section

        """
        if self.k['x_pre'] == self.k['x_suc'] \
                and self.k['y_pre'] == -self.k['y_suc'] \
                and self.k['th_suc'] == -self.k['th_pre'] \
                and self.k['d2ydx2_pre'] == -self.k['d2ydx2_suc'] \
                and self.k['yte'] == 0:
            return True
        else:
            return False

    def is_valid(self):
        r"""Check that the geometry is valid and corresponds to a 2D section 
        that can actually be built.

        Returns
        -------
        boolean : True for a valid section, False for an invalid section

        Raises
        ------
        NotImplementedError for a section that is not symmetrical

        """

        if self.is_symmetrical() is True:
            # Basic checks
            if self.k["rle"] < 0:
                return False
            if self.k["x_pre"] < 0 or self.k["x_suc"] < 0:
                return False
            if self.k["y_pre"] >= 0 or self.k["y_suc"] <= 0:
                return False
            if self.k['d2ydx2_pre'] < 0 or self.k['d2ydx2_suc'] > 0:
                return False
            if self.k['th_pre'] < 0 or self.k['th_suc'] > 0:
                return False

            x_l, y_l, x_u, y_u = self.get_coords()[:4]

            # Check that the pressure side or the suction side
            # do not cross the y=0 axis
            # the sign of the y coordinates does not change
            sign_changes_suc = len(list(groupby(y_u, lambda ys: ys >= 0))) - 1
            sign_changes_pre = len(list(groupby(y_l, lambda ys: ys <= 0))) - 1

            max_y_coord = max(y_u)
            min_y_coord = min(y_l)

            real_thickness = max_y_coord - min_y_coord
            assert real_thickness > 0.

            if sign_changes_suc > 0:
                return False
            elif sign_changes_pre > 0:
                return False
            # Check if the real thickness is not greater
            # than the specified thickness
            # test for this validity condition (the goal is to dismiss
            # fat-ass foils in optimization procedures
            elif real_thickness > 1.1 * (self.k['y_suc'] - self.k['y_pre']):
                return False
            else:
                return True

        else:  # section is not symmetrical
            raise NotImplementedError
