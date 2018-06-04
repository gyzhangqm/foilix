# coding: utf-8

r"""Foil polars"""

from __future__ import division, print_function

import logging
from os.path import basename, splitext

import numpy as np
import scipy.interpolate

from foilix.data_api import get_data_tuple

from foilix.xfoil.xfoil import oper_visc_alpha
# from foilix.db_deprecated.query import data_from_db

logger = logging.getLogger(__name__)


def build_interpolator(x, y):
    r"""Function to make interpolation logic switching easy"""
    # min drag from symmetrical is not at 0
    # return scipy.interpolate.Akima1DInterpolator(x, y)

    return scipy.interpolate.PchipInterpolator(x, y)

    # return scipy.interpolate.interp1d(x, y, kind="linear")

    # min drag from symmetrical is not at 0
    # return scipy.interpolate.interp1d(x, y, kind="cubic")


class Polar(object):
    r"""Convenience wrapper for the polar returned by _oper_visc

    Parameters
    ----------
    foil_data_folder : str
        Path to the foil data folder (precomputed data)
    filename : String
        The name of the .dat file containing the airfoil coordinates
    angles_of_attack_spec : list of 3 floats [start, stop, interval]
        The angles of attack at which the foil should be evaluated
    reynolds_number : float
        The Reynolds number at which the foil should be evaluated
    ncrit : float
        The Ncrit value (turbulence level) to be used for xfoil calculations
    use_precomputed_data : bool
        if False, compute the values
        if True, retrieve the values from the database

    Returns
    -------
    polar : array
        The return value of a call to _oper_visc()

    """
    def __init__(self,
                 foil_data_folder,
                 filename,
                 angles_of_attack_spec,
                 reynolds_number,
                 ncrit,
                 iterlim=200,
                 use_precomputed_data=False):
        self.foil_data_folder = foil_data_folder
        self._filename = filename

        # [start, stop, interval]}
        self._angles_of_attack_spec = angles_of_attack_spec

        self._reynolds_number = reynolds_number
        self._iterlim = iterlim
        self._ncrit = ncrit
        self.use_precomputed_data = use_precomputed_data

        self.computed = False

        self._oper_visc_alpha_result = None
        self._data_array = np.empty(shape=(0, 7))
        # print(self._data_array)
        self._data_header = None
        self._infodict = None
        self._warnings = list()

    def compute(self):
        r"""Compute the polar"""
        if self.use_precomputed_data is False:  # compute the values
            self._data_array, self._data_header, self._infodict, self._warnings = \
                oper_visc_alpha(self._filename,
                                self._angles_of_attack_spec,
                                self._reynolds_number,
                                iterlim=self._iterlim,
                                show_seconds=0,
                                n_crit=self._ncrit)
        # else:  # use db_deprecated
        #     for angle in self.angles_of_attack_spec:
        #         data = data_from_db(self._filename,
        #                             angle,
        #                             self._reynolds_number,
        #                             self._ncrit,
        #                             0.)
        #
        #         if data is not None:
        #             cl, cd, cdp, cm, top_xtr, bot_xtr = data
        #
        #             self._data_array = np.append(self._data_array,
        #                                          [[angle,
        #                                            cl,
        #                                            cd,
        #                                            cdp,
        #                                            cm,
        #                                            top_xtr,
        #                                            bot_xtr]],
        #                                          axis=0)

        else:
            foil_id = splitext(basename(self._filename))[0]

            for angle in self.angles_of_attack_spec:

                cl, cd, cdp, cm, top_xtr, bot_xtr = get_data_tuple(self.foil_data_folder,
                                                                   foil_id,
                                                                   mach=0,
                                                                   ncrit=self._ncrit,
                                                                   reynolds=self._reynolds_number,
                                                                   aoa=angle)
                self._data_array = np.append(self._data_array,
                                             [[angle,
                                               cl,
                                               cd,
                                               cdp,
                                               cm,
                                               top_xtr,
                                               bot_xtr]],
                                             axis=0)

        self.computed = True

    @property
    def interp_aoas(self):
        r"""list of aoa for curve smoothing/interpolation

        1001 was really slowing down the application.
        101 seems to be a good compromise

        """
        # assert self.computed is True
        if self.computed is False:
            msg = "The Polar should have been computed before " \
                  "calling interp_aoas"
            logger.error(msg)
            raise AssertionError(msg)
        return np.linspace(np.min(self.angles_of_attack_computed),
                           np.max(self.angles_of_attack_computed),
                           num=101)

    @property
    def warnings(self):
        r"""Warnings generated by the polar computation

        Returns
        -------
        list

        """
        # assert self.computed is True
        if self.computed is False:
            msg = "The Polar should have been computed before calling warnings"
            logger.error(msg)
            raise AssertionError(msg)
        return [w.encode().strip() for w in self._warnings]

    # def append_warning(self, message):
    #     self._warnings.append(message)

    @property
    def angles_of_attack_spec(self):
        r"""List of angles of attack

        Returns
        -------
        ndarray
            Array of angles of attack where the polar is to be computed

        """
        return np.arange(self._angles_of_attack_spec[0],
                         self._angles_of_attack_spec[1],
                         self._angles_of_attack_spec[2])

    @property
    def angles_of_attack_computed(self):
        r"""Angles of attack that have been computed"""
        # assert self.computed is True
        if self.computed is False:
            msg = "The Polar should have been computed before " \
                  "calling angles_of_attack_computed"
            logger.error(msg)
            raise AssertionError(msg)
        return self._data_array[:, 0]

    @property
    def coefficients_of_lift(self):
        r"""Coefficient of lift for each angle of attack

        Returns
        -------
        A list of coefficients of lift in the same order as
        self.angles_of_attack

        """
        # assert self.computed is True
        if self.computed is False:
            msg = "The Polar should have been computed before " \
                  "calling coefficients_of_lift"
            logger.error(msg)
            raise AssertionError(msg)
        return self._data_array[:, 1]

    @property
    def coefficients_of_lift_interpolator(self):
        r"""Interpolator for the coefficient of lift"""
        logger.debug("self.angles_of_attack_computed : %s" %
                     self.angles_of_attack_computed)
        logger.debug("self.self.coefficients_of_lift : %s" %
                     self.coefficients_of_lift)
        # return scipy.interpolate.interp1d(self.angles_of_attack_computed,
        #                                   self.coefficients_of_lift,
        #                                   kind="cubic")
        return build_interpolator(self.angles_of_attack_computed,
                                  self.coefficients_of_lift)

    @property
    def coefficients_of_drag(self):
        r"""Coefficient of drag for each angle of attack

        Returns
        -------
        A list of coefficients of drag
        in the same order as self.angles_of_attack

        """
        # assert self.computed is True
        if self.computed is False:
            msg = "The Polar should have been computed before " \
                  "calling coefficients_of_drag"
            logger.error(msg)
            raise AssertionError(msg)
        return self._data_array[:, 2]

    @property
    def coefficients_of_drag_interpolator(self):
        r"""Interpolator for the coefficient of drag"""
        # return scipy.interpolate.interp1d(self.angles_of_attack_computed,
        #                                   self.coefficients_of_drag,
        #                                   kind="cubic")
        return build_interpolator(self.angles_of_attack_computed,
                                  self.coefficients_of_drag)

    @property
    def lift_to_drag(self):
        r"""Lift to drag for each angle of attack

        Returns
        -------
        A list of lift to drag ratios in the same order as self.angles_of_attack
        """
        return self.coefficients_of_lift / self.coefficients_of_drag

    @property
    def lift_to_drag_interpolator(self):
        r"""Interpolator for the L/D ratio"""
        # return scipy.interpolate.interp1d(self.angles_of_attack_computed,
        #                                   self.lift_to_drag,
        #                                   kind="cubic")
        return build_interpolator(self.angles_of_attack_computed,
                                  self.lift_to_drag)

    @property
    def maximum_lift(self):
        r"""Maximum lift

        Returns
        -------
        tuple(float, float)
            Maximum lift, angle of attack at maximum lift

        """
        coefs_lift = [self.coefficients_of_lift_interpolator(aoa)
                      for aoa in self.interp_aoas]
        return np.max(coefs_lift), self.interp_aoas[np.argmax(coefs_lift)]
        # return np.max(self.coefficients_of_lift), \
        #        self.angles_of_attack[np.argmax(self.coefficients_of_lift)]

    @property
    def minimum_drag(self):
        r"""Minimum drag

        Returns
        -------
        tuple(float, float)
            Minimum drag, angle of attack at minimum drag

        """
        coefs_drag = [self.coefficients_of_drag_interpolator(aoa)
                      for aoa in self.interp_aoas]
        return np.min(coefs_drag), self.interp_aoas[np.argmin(coefs_drag)]
        # return np.min(self.coefficients_of_drag),
        #        self.angles_of_attack[np.argmin(self.coefficients_of_drag)]

    @property
    def max_lift_to_drag(self):
        r"""Maximum lift to drag

        Returns
        -------
        tuple(float, float)
            Maximum lift to drag, angle of attack at maximum lift to drag

        """
        l_to_d = [self.lift_to_drag_interpolator(aoa)
                  for aoa in self.interp_aoas]
        return np.max(l_to_d), self.interp_aoas[np.argmax(l_to_d)]
        # return np.max(self.lift_to_drag),
        #        self.angles_of_attack[np.argmax(self.lift_to_drag)]


class PolarMatrix(object):
    r"""A 2D array of Polar objects

    Parameters
    ----------
    reynolds_numbers : list[float]
        List of reynolds numbers at which the polars are evaluated
    ncrits : list|float]
        List of n_crit parameters at which the polars are evaluated
    use_db : bool
        Compute or use the database

    """

    def __init__(self,
                 foil_data_folder,
                 filename,
                 angles_of_attack_spec,
                 reynolds_numbers,
                 ncrits,
                 iterlim=200,
                 use_precomputed_data=False):
        self.foil_data_folder = foil_data_folder
        self._filename = filename

        # [start, stop, interval]}
        self._angles_of_attack_spec = angles_of_attack_spec

        self._reynolds_numbers = reynolds_numbers
        self._iterlim = iterlim
        self._ncrits = ncrits
        self.use_precomputed_data = use_precomputed_data

        self.matrix = list()

        self.computed = False

    def compute(self):
        r"""Compute a polar for each Rn / ncrit combination.
        Store the results in the 2d (Rn, ncrit) polar matrix"""
        for rn in self._reynolds_numbers:
            polars_for_given_reynolds = list()
            for nc in self._ncrits:
                polar = Polar(self.foil_data_folder,
                              self._filename,
                              self._angles_of_attack_spec,
                              rn,
                              nc,
                              self._iterlim,
                              use_precomputed_data=self.use_precomputed_data)
                polar.compute()
                polars_for_given_reynolds.append(polar)
            self.matrix.append(polars_for_given_reynolds)

        self.computed = True

    @property
    def avg_max_lift(self):
        r"""Average maximum lift in the matrix of polars

        Returns
        -------
        (float, float)
            Average maximum lift, average angle at maximum lift

        """
        accumulator_value = 0
        accumulator_angle = 0
        count = 0
        for i, _ in enumerate(self._reynolds_numbers):
            for j, _ in enumerate(self._ncrits):
                accumulator_value += self.matrix[i][j].maximum_lift[0]
                accumulator_angle += self.matrix[i][j].maximum_lift[1]
                count += 1
        return accumulator_value / count, accumulator_angle / count

    def avg_lift(self, angle_of_attack):
        r"""Average lift at the specified angle of attack

        Parameters
        ----------
        angle_of_attack : float
            The angle of attack for which the lift average is to be computed.

        Returns
        -------
        float
            Average lift at the specified angle of attack

        """
        accumulator_value = 0
        count = 0
        for i, rn in enumerate(self._reynolds_numbers):
            for j, nc in enumerate(self._ncrits):
                accumulator_value += self.matrix[i][j].coefficients_of_lift_interpolator(angle_of_attack)
                count += 1
        return accumulator_value / count

    @property
    def avg_max_lift_to_drag(self):
        r"""Average maximum L/D in the matrix of polars

        Returns
        -------
        (float, float)
            Average maximum L/D, average angle at maximum L/D

        """
        accumulator_value = 0
        accumulator_angle = 0
        count = 0
        for i, rn in enumerate(self._reynolds_numbers):
            for j, nc in enumerate(self._ncrits):
                accumulator_value += self.matrix[i][j].max_lift_to_drag[0]
                accumulator_angle += self.matrix[i][j].max_lift_to_drag[1]
                count += 1
        return accumulator_value / count, accumulator_angle / count

    def avg_lift_to_drag(self, angle_of_attack):
        r"""Average L/D in the matrix of polars at the specified angle of attack

        Parameters
        ----------
        angle_of_attack : float
            The angle of attack for which the L/D average is to be computed.

        Returns
        -------
        float
            Average L/D at the specified angle of attack

        """
        accumulator_value = 0
        count = 0
        for i, rn in enumerate(self._reynolds_numbers):
            for j, nc in enumerate(self._ncrits):
                accumulator_value += self.matrix[i][j].lift_to_drag_interpolator(angle_of_attack)
                count += 1
        return accumulator_value / count

    @property
    def avg_min_drag(self):
        r"""Average minimum drag in the matrix of polars

        Returns
        -------
        (float, float)
            Average minimum drag, average angle at minimum drag

        """
        accumulator_value = 0
        accumulator_angle = 0
        count = 0
        for i, rn in enumerate(self._reynolds_numbers):
            for j, nc in enumerate(self._ncrits):
                accumulator_value += self.matrix[i][j].minimum_drag[0]
                accumulator_angle += self.matrix[i][j].minimum_drag[1]
                count += 1
        return accumulator_value / count, accumulator_angle / count
