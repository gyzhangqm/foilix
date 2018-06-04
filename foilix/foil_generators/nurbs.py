# coding: utf-8

r"""Generates airfoil using NURBS.

Original Paper: http://eprints.soton.ac.uk/50031/1/Sobe07.pdf

"""

from __future__ import print_function, division

import math  # write math.pow instead of pow for clarity (not pow builtin)
from math import cos, sin, pi

import numpy as np

from foilix.foil_generators.parametric_foil import ParametricFoil


class NURBS(ParametricFoil):
    r"""NURBS foil parameterization

    Takes a dictionary of coefficients to define NURBS airfoil.
    Coefficient names:
    ta_u
    ta_l
    tb_u
    tb_l
    alpha_b
    alpha_c

    Parameters
    ----------
    k : dict

    """
    def __init__(self, k):
        # The validity of parameters is checked by the the
        # is_valid() function, not here
        # The conversions to float will raise a ValueError
        # when the conversion cannot be performed
        # but the logic to check that the parameters have reasonable values
        # are in the is_valid() function
        self.k = k

        self.ta_u = float(k['ta_u'])
        self.ta_l = float(k['ta_l'])
        self.tb_u = float(k['tb_u'])
        self.tb_l = float(k['tb_l'])
        self.alpha_b = float(k['alpha_b'])
        self.alpha_c = float(k['alpha_c'])

    def _spline(self):
        r"""Calculates the spline interpolation for the airfoil
        params specified"""
        u = np.linspace(0, 1, 100)
        x_u, y_u, x_l, y_l = list(), list(), list(), list()
        temp_var1 = np.array([[1, 0, 0, 0],
                              [0, 0, 1, 0],
                              [-3, 3, -2, -1],
                              [2, -2, 1, 1]])
        A = [0, 0]
        B = [1, 0]
        ta_u = self.ta_u
        ta_l = self.ta_l
        tb_u = self.tb_u
        tb_l = self.tb_l
        alpha_b = self.alpha_b
        alpha_c = self.alpha_c

        # initialize end tangent magnitudes and directions
        TA_u = [(ta_u * cos(-pi/2)),
                ta_u * abs(sin(-pi/2))]
        TB_u = [(tb_u * cos(-((alpha_c + alpha_b) * pi/180))),
                (tb_u * sin(-((alpha_b + alpha_c) * pi/180)))]
        TA_l = [(ta_l * cos(-pi/2)),
                ta_l * (sin(-pi/2))]
        TB_l = [(tb_l * cos(-(alpha_c * pi/180))),
                (tb_l * sin(-(alpha_c * pi/180)))]

        # calculate (x,y) for the upper curve of the airfoil
        for j in range(2):
            # control points for x and y coords
            temp_var = np.array([[A[j]], [B[j]], [TA_u[j]], [TB_u[j]]])

            temp_var_coord = np.dot(temp_var1, temp_var)
            for value in u:
                temp_var4 = [1, value, value**2, math.pow(value, 3)]
                if j == 1:
                    # calculate x coords
                    x_u.append(float(np.dot(temp_var4, temp_var_coord)))
                else:
                    # calculate y coords
                    y_u.append(float(np.dot(temp_var4, temp_var_coord)))

        # calculate (x,y) for the lower curve of the airfoil
        for j in range(2):
            # control points for x and y coords
            temp_var = np.array([[A[j]], [B[j]], [TA_l[j]], [TB_l[j]]])

            temp_var_coord = np.dot(temp_var1, temp_var)
            for value in u:
                temp_var4 = [1, value, value**2, math.pow(value, 3)]
                if j == 1:
                    # calculate x coords
                    x_l.append(float(np.dot(temp_var4, temp_var_coord)))
                else:
                    # calculate y coords
                    y_l.append(float(np.dot(temp_var4, temp_var_coord)))
        # coords = np.array([x_u,y_u,x_l,y_l])
        # coords = np.array([x_u, y_u, x_l, y_l])
        # return coords
        # return x_l, y_l, x_u, y_u
        return np.array(x_l), np.array(y_l), np.array(x_u), np.array(y_u)

    def is_symmetrical(self):
        r"""Check if the section is symmetrical.

        This is the implementation of the abstract method of ParametricFoil

        Returns
        -------
        boolean : True for a symmetrical section,
                  False for an assymetrical section

        """
        if self.ta_u == self.ta_l \
                and self.tb_u == self.tb_l \
                and self.alpha_b == -2 * self.alpha_c:
            return True
        else:
            return False

    def is_valid(self):
        r"""Check that the geometry is valid and corresponds to a
        2D section that can actually be built.

        Returns
        -------
        boolean : True for a valid section, False for an invalid section

        """
        # The checks are a duplicate from the __init__() parameters check
        if self.ta_l >= 0. \
                and self.ta_u >= 0. \
                and self.tb_u >= 0 \
                and self.tb_l >= 0. \
                and self.alpha_b >= 0:
            return True
        else:
            return False

    def _fn_upper_lower(self, xpts):
        r"""This is the implementation of the abstract method of ParametricFoil

        Parameters
        ----------
        xpts

        Returns
        -------

        """
        # sp = self._spline()
        x_u, y_u, x_l, y_l = self._spline()
        # x_u = sp[0]
        # y_u = sp[1]
        # x_l = sp[2]
        # y_l = sp[3]
        # return y_l, x_l, y_u, x_u,
        return y_u, x_u, y_l, x_l,
        # return x_u, y_u, x_l, y_l,

    def _camberline(self, xpts):
        raise NotImplementedError

    def _thickness(self, xpts):
        raise NotImplementedError

    def __str__(self):
        """Gives some information on foil"""
        return "Airfoil with NURBS parametrization. " \
               "Coefficients: {}".format(self.k)
