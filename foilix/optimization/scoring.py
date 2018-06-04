# coding: utf-8

r"""Scoring logic for PSO algorithms

The code (e.g. FoilSectionScorer) deals with 2d foil sections scoring
but it could be anything else as long as it subclasses the Scorer
abstract base class

"""

from __future__ import division

import logging
import abc
import os
import shutil
import string
import random

import numpy as np

import foilix.xfoil.polar
import foilix.xfoil.xfoil
import foilix.foil_generators.parsec
import foilix.foil_generators.nurbs

logger = logging.getLogger(__name__)


class Scorer(object):
    r"""Base class for all scoring objects
    that can be used by the PsoAlgorithm"""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def score(self, pts):
        r"""The score method transforms the pts array of values into a score

        Subclasses must implement the score method

        Parameters
        ----------
        pts

        """
        raise NotImplementedError


class CompoundScoreSectionScorer(Scorer):
    r"""Scorer object for a symmetrical foil section

    Parameters
    ----------
    thickness : float, strictly positive, between 0.0 (excluded) and 0.3
        thickness for a unit length foil chord
        (i.e. 0.06 denotes a 6% thick foil)
    angles_of_attack : list[float], list of 3 positive floats
        min, max and step
    reynolds: list[float], list of positive floats
        reynolds numbers at which evaluation should take place
    ncrits : list[positive float]
        xfoil ncrits
    iterlim : int
        xfoil iterlim (maximum number of iterations in xfoil 
                       to reach convergence)
    max_lift_scaling : float, optional
        multiplier of maximum lift
    inv_min_drag_scaling : float, optional
        multiplier of the inverse of minimum drag
    max_lift_to_drag_scaling : float, optional
        multiplier of the maximum lift to drag
    max_lift_weight : float, optional
        weight of max lift in the scoring logic
    min_drag_weight : float, optional
        weight of min drag in the scoring logic
    max_lift_to_drag_weight : float, optional
        weight of max L/D in the scoring logic
    """
    def __init__(self,
                 thickness,
                 angles_of_attack,
                 reynolds,
                 ncrits,
                 iterlim,
                 max_lift_scaling=30.,
                 inv_min_drag_scaling=0.3,
                 max_lift_to_drag_scaling=1.,
                 max_lift_weight=1.,
                 min_drag_weight=1.,
                 max_lift_to_drag_weight=1.):
        # thickness
        # assert thickness > 0.
        if thickness <= 0.:
            msg = "thickness should be strictly positive"
            raise ValueError(msg)
        # assert thickness <= 0.3
        if thickness > 0.3:
            msg = "A thickness greater than 0.3 is not realistic"
            raise ValueError(msg)

        # angle of attack checks
        start, end, step = angles_of_attack
        # assert start >= 0
        if start < 0:
            msg = "start aoa value should be positive or zero"
            raise ValueError(msg)
        # assert start < end
        if start >= end:
            msg = "start aoa should be strictly less than end aoa"
            raise ValueError(msg)
        # assert step > 0.
        if step <= 0.:
            msg = "aoa step should be strictly positive"
            raise ValueError(msg)
        # assert step < end - start
        if step >= end - start:
            msg = "aoa step should be strictly less than the difference " \
                  "between aoa end and aos start"
            raise ValueError(msg)

        # reynolds checks
        for r in reynolds:
            # assert r > 0
            if r <= 0:
                msg = "One of the Reynolds numbers is not strictly positive"
                raise ValueError(msg)

        # ncrit checks
        for ncrit in ncrits:
            # assert ncrit > 0.
            if ncrit <= 0.:
                msg = "One of the ncrits is not strictly positive"
                raise ValueError(msg)
            # assert ncrit < 20.
            if ncrit >= 20.:
                msg = "One of the ncrits is not realistic"
                raise ValueError(msg)

        # iterlim checks
        # assert iterlim > 0 and type(iterlim) is int
        if not (iterlim > 0 and type(iterlim) is int):
            msg = "iterlim should be a strictly positive integer"
            raise ValueError(msg)

        # scoring scaling factors ans weights checks
        # assert max_lift_scaling >= 0.0
        if max_lift_scaling < 0.:
            msg = "max_lift_scaling should be positive or zero"
            raise ValueError(msg)
        # assert inv_min_drag_scaling >= 0.0
        if inv_min_drag_scaling < 0.:
            msg = "inv_min_drag_scaling should be positive or zero"
            raise ValueError(msg)
        # assert max_lift_to_drag_scaling >= 0.0
        if max_lift_to_drag_scaling < 0.:
            msg = "max_lift_to_drag_scaling should be positive or zero"
            raise ValueError(msg)
        # assert max_lift_weight >= 0.0
        if max_lift_weight < 0.:
            msg = "max_lift_weight should be positive or zero"
            raise ValueError(msg)
        # assert min_drag_weight >= 0.0
        if min_drag_weight < 0.:
            msg = "min_drag_weight should be positive or zero"
            raise ValueError(msg)
        # assert max_lift_to_drag_weight >= 0.0
        if max_lift_to_drag_weight < 0.:
            msg = "max_lift_to_drag_weight should be positive or zero"
            raise ValueError(msg)

        self.thickness = thickness

        self.angles_of_attack = angles_of_attack
        self.reynolds = reynolds
        self.ncrits = ncrits
        self.iterlim = iterlim

        self.max_lift_scaling = max_lift_scaling
        self.inv_min_drag_scaling = inv_min_drag_scaling
        self.max_lift_to_drag_scaling = max_lift_to_drag_scaling
        self.max_lift_weight = max_lift_weight
        self.min_drag_weight = min_drag_weight
        self.max_lift_to_drag_weight = max_lift_to_drag_weight

        self.tmp_dir = "./tmp_%s" % str(random.randint(0, 100000))
        os.mkdir(self.tmp_dir)

    def construct_symmetrical_airfoil(self, pts):
        r"""Build the symmetrical foil section for pts (list of 4 values)

        Parameters
        ----------
        pts : list[float]
            The list of 4 values that define the PARSEC foil section

        """
        k = {}
        k['rle'] = pts[0]
        k['x_pre'] = pts[1]
        # Thickness 6%
        k['y_pre'] = -self.thickness / 2.0
        k['d2ydx2_pre'] = -pts[2]
        # Trailing edge angle
        k['th_pre'] = pts[3]
        # Suction part
        k['x_suc'] = k['x_pre']
        k['y_suc'] = -k['y_pre']
        k['d2ydx2_suc'] = -k['d2ydx2_pre']
        k['th_suc'] = -k['th_pre']
        # Trailing edge x and y position
        k['xte'] = 1.0  # beware of PARSEC generator check
        k['yte'] = 0.0

        return foilix.foil_generators.parsec.PARSEC(k)

    def score(self, pts):
        r"""Compute the foil score

        Parameters
        ----------
        pts : list[float]
            The list of 4 values that define the PARSEC foil section

        Returns
        -------
        float or None

        """
        # assert len(pts) == 4
        if len(pts) != 4:
            msg = "Expected 4 PARSEC parameters, found %i" % len(pts)
            logger.error(msg)
            raise ValueError(msg)

        foil = self.construct_symmetrical_airfoil(pts)

        # check the airfoil is symmetrical and valid
        if foil.is_symmetrical() is False:
            logger.info("Foil is not symmetrical, score is None")
            return None
        if foil.is_valid() is False:
            logger.info("Foil is not valid, score is None")
            return None

        # Make unique filename
        randstr = ''.join(random.choice(string.ascii_uppercase)
                          for _ in range(20))
        filename = "parsec_{}.dat".format(randstr)
        logger.info("Filename : %s" % filename)

        with open(filename, 'w') as af:
            af.write(foil.get_coords_plain())  # Save coordinates

        try:
            # instantiating XFoilScorer trigger the run() method of XFoilPilot
            # scorer = foilix.xfoil.xfoil.XFoilScorer(pilot)
            matrix = foilix.xfoil.polar.PolarMatrix("",
                                                    filename,
                                                    self.angles_of_attack,
                                                    self.reynolds,
                                                    self.ncrits,
                                                    self.iterlim,
                                                    use_precomputed_data=False)
            matrix.compute()

            try:
                score = compound_score(matrix.avg_max_lift[0],
                                       matrix.avg_min_drag[0],
                                       matrix.avg_max_lift_to_drag[0],
                                       self.max_lift_scaling,
                                       self.inv_min_drag_scaling,
                                       self.max_lift_to_drag_scaling,
                                       self.max_lift_weight,
                                       self.min_drag_weight,
                                       self.max_lift_to_drag_weight)
            except TypeError:
                # has something to do with scipy interpolation ??
                logger.debug("A TypeError occurred")
                return None

            if score < 0:
                return None

            if score is not None:
                score = 1. / score

            if np.isfinite(score):  # If it's not NaN
                logger.debug("Return score")
                return score
            else:
                logger.debug("Return None")
                return None
        except IndexError:
            logger.error("Return None (IndexError)")
            return None
        except ValueError:
            logger.error("Return None (ValueError)")
            return None
        finally:
            try:
                shutil.copyfile(filename, "%s/%s" % (self.tmp_dir, filename))
                logger.info("Removing : %s" % filename)
                os.remove(filename)
            except WindowsError:
                logger.error("\n\n\n\nWindows was not capable of removing "
                             "the file.\n\n\n\n")


class YachtAppendageSectionScorer(Scorer):
    r"""Scorer object for a symmetrical foil section

    Parameters
    ----------
    angles_of_attack : list[float], list of 3 positive floats
        min, max and step
    aoa_ld : list[float]
        List of aoa for L/D scoring
    reynolds: list[float], list of positive floats
        reynolds numbers at which evaluation should take place
    ncrits : list[positive float]
        xfoil ncrits
    iterlim : int
        xfoil iterlim (maximum number of iterations in xfoil to 
                       reach convergence)
    inv_min_drag_scaling : float, optional
        multiplier of the inverse of minimum drag

    """
    def __init__(self,
                 angles_of_attack,
                 aoa_ld,
                 reynolds,
                 ncrits,
                 iterlim,
                 inv_min_drag_scaling=0.3):

        # angle of attack checks
        start, end, step = angles_of_attack
        # assert start >= 0
        if start < 0:
            msg = "start aoa value should be positive or zero"
            raise ValueError(msg)
        # assert start < end
        if start >= end:
            msg = "start aoa should be strictly less than end aoa"
            raise ValueError(msg)
        # assert step > 0.
        if step <= 0.:
            msg = "aoa step should be strictly positive"
            raise ValueError(msg)
        # assert step < end - start
        if step >= end - start:
            msg = "aoa step should be strictly less than the difference " \
                  "between aoa end and aos start"
            raise ValueError(msg)

        # reynolds checks
        for r in reynolds:
            # assert r > 0
            if r <= 0:
                msg = "One of the Reynolds numbers is not strictly positive"
                raise ValueError(msg)

        # ncrit checks
        for ncrit in ncrits:
            # assert ncrit > 0.
            if ncrit <= 0.:
                msg = "One of the ncrits is not strictly positive"
                raise ValueError(msg)
            # assert ncrit < 20.
            if ncrit >= 20.:
                msg = "One of the ncrits is not realistic"
                raise ValueError(msg)

        # iterlim checks
        # assert iterlim > 0 and type(iterlim) is int
        if not (iterlim > 0 and type(iterlim) is int):
            msg = "iterlim should be a strictly positive integer"
            raise ValueError(msg)

        # scoring scaling factors ans weights checks
        # assert inv_min_drag_scaling >= 0.0
        if inv_min_drag_scaling < 0.:
            msg = "inv_min_drag_scaling should be positive or zero"
            raise ValueError(msg)

        self.angles_of_attack = angles_of_attack
        self.aoa_ld = aoa_ld
        self.reynolds = reynolds
        self.ncrits = ncrits
        self.iterlim = iterlim

        self.inv_min_drag_scaling = inv_min_drag_scaling

        self.tmp_dir = "./tmp_%s" % str(random.randint(0, 100000))
        os.mkdir(self.tmp_dir)

    # @staticmethod
    # def construct_symmetrical_airfoil(pts):
    #     r"""Build the symmetrical foil section for pts (list of 4 values)
    #
    #     Parameters
    #     ----------
    #     pts : list[float]
    #         The list of 5 values that define the PARSEC foil section
    #         thickness, le radius, x max thickness, curvature, te angle
    #
    #     """
    #     k = {}
    #     k['rle'] = pts[1]
    #     k['x_pre'] = pts[2]
    #     # Thickness 6%
    #     k['y_pre'] = -pts[0] / 2.0
    #     k['d2ydx2_pre'] = -pts[3]
    #     # Trailing edge angle
    #     k['th_pre'] = pts[4]
    #     # Suction part
    #     k['x_suc'] = k['x_pre']
    #     k['y_suc'] = -k['y_pre']
    #     k['d2ydx2_suc'] = -k['d2ydx2_pre']
    #     k['th_suc'] = -k['th_pre']
    #     # Trailing edge x and y position
    #     k['xte'] = 1.0  # beware of PARSEC generator check
    #     k['yte'] = 0.0
    #
    #     return foilix.foil_generators.parsec.PARSEC(k)

    def score(self, pts):
        r"""Compute the foil score

        Parameters
        ----------
        pts : list[float]
            The list of 4 values that define the PARSEC foil section

        Returns
        -------
        float or None

        """
        # assert len(pts) == 5

        foil = self.construct_symmetrical_airfoil(pts)

        # check the airfoil is symmetrical and valid
        if foil.is_symmetrical() is False:
            logger.info("Foil is not symmetrical, score is None")
            return None
        if foil.is_valid() is False:
            logger.info("Foil is not valid, score is None")
            return None

        # Make unique filename
        randstr = ''.join(random.choice(string.ascii_uppercase)
                          for _ in range(20))
        filename = "parsec_{}.dat".format(randstr)
        logger.info("Filename : %s" % filename)

        with open(filename, 'w') as af:
            af.write(foil.get_coords_plain())  # Save coordinates

        try:
            # instantiating XFoilScorer trigger the run() method of XFoilPilot
            # scorer = foilix.xfoil.xfoil.XFoilScorer(pilot)
            matrix = foilix.xfoil.polar.PolarMatrix("",  # who cares about precomputed data !
                                                    filename,
                                                    self.angles_of_attack,
                                                    self.reynolds,
                                                    self.ncrits,
                                                    self.iterlim,
                                                    use_precomputed_data=False)
            matrix.compute()

            try:
                avg_min_drag, avg_min_drag_angle = matrix.avg_min_drag
                score = yacht_appendage_scoring([matrix.avg_lift_to_drag(angle)
                                                 for angle in self.aoa_ld],
                                                avg_min_drag,
                                                self.inv_min_drag_scaling)
            except TypeError:
                # has something to do with scipy interpolation ??
                logger.debug("A TypeError occurred")
                return None

            if score < 0:
                return None

            if score is not None:
                score = 1. / score

            if np.isfinite(score):  # If it's not NaN
                logger.debug("Return score")
                return score
            else:
                logger.debug("Return None")
                return None
        except IndexError:
            logger.error("Return None (IndexError)")
            return None
        except ValueError:
            logger.error("Return None (ValueError)")
            return None
        finally:
            try:
                shutil.copyfile(filename, "%s/%s" % (self.tmp_dir, filename))
                logger.info("Removing : %s" % filename)
                os.remove(filename)
            except WindowsError:
                logger.error("\n\n\n\nWindows was not capable of removing "
                             "the file.\n\n\n\n")


class YachtAppendageParsecSectionScorer(YachtAppendageSectionScorer):
    r"""PARSEC version of yacht appendage scorer"""
    def __init__(self,
                 angles_of_attack,
                 aoa_ld,
                 reynolds,
                 ncrits,
                 iterlim,
                 inv_min_drag_scaling=0.3):
        super(YachtAppendageParsecSectionScorer, self).__init__(angles_of_attack,
                                                                aoa_ld,
                                                                reynolds,
                                                                ncrits,
                                                                iterlim,
                                                                inv_min_drag_scaling=inv_min_drag_scaling)
        self.parameterization_type = "SYM_PARSEC"

    @staticmethod
    def construct_symmetrical_airfoil(pts):
        r"""Build the symmetrical foil section for pts (list of 4 values)

        Parameters
        ----------
        pts : list[float]
            The list of 5 values that define the PARSEC foil section
            thickness, le radius, x max thickness, curvature, te angle

        """
        k = {}
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

        return foilix.foil_generators.parsec.PARSEC(k)


class YachtAppendageNurbsSectionScorer(YachtAppendageSectionScorer):
    r"""NURBS version of yacht appendage scorer"""
    def __init__(self,
                 angles_of_attack,
                 aoa_ld,
                 reynolds,
                 ncrits,
                 iterlim,
                 inv_min_drag_scaling=0.3):
        super(YachtAppendageNurbsSectionScorer, self).__init__(angles_of_attack,
                                                               aoa_ld,
                                                               reynolds,
                                                               ncrits,
                                                               iterlim,
                                                               inv_min_drag_scaling=inv_min_drag_scaling)
        self.parameterization_type = "SYM_NURBS"

    @staticmethod
    def construct_symmetrical_airfoil(pts):
        r"""Build the symmetrical foil section for pts (list of 4 values)

        Parameters
        ----------
        pts : list[float]
            The list of 5 values that define the PARSEC foil section
            thickness, le radius, x max thickness, curvature, te angle

        """
        ta = pts[0]
        tb = pts[1]
        alpha = pts[2]
        k = {'ta_u': ta,
             'ta_l': ta,
             'tb_u': tb,
             'tb_l': tb,
             'alpha_b': 2*alpha,
             'alpha_c': -alpha}

        return foilix.foil_generators.nurbs.NURBS(k)


def yacht_appendage_scoring(list_of_lift_to_drag,
                            min_drag,
                            inv_min_drag_scaling):
    r"""Yacht appendage scoring method

    Average of L/D at specified angles + scoring * (1 / average of min drag)

    Average L/D typical value at low Re (15 -> 60 k reynolds): 18
    Average inv min drag value: 45

    Parameters
    ----------
    list_of_lift_to_drag : list[float]
        The L/D ratios
    min_drag : float
        The minimum drag
    inv_min_drag_scaling : float
        The scaling of minimum drag against L/D average

    """
    logger.debug("Scoring for %i lift_to_drag" % len(list_of_lift_to_drag))
    logger.debug("list_of_lift_to_drag : %s" % str(list_of_lift_to_drag))
    avg_ld = sum(list_of_lift_to_drag) / len(list_of_lift_to_drag)
    logger.debug("avg_ld : %f" % avg_ld)
    logger.debug("min_drag : %f" % min_drag)
    logger.debug("inv_min_drag_scaling : %f" % inv_min_drag_scaling)
    logger.debug("score : %f" %
                 (avg_ld + (1 / min_drag) * inv_min_drag_scaling))

    return avg_ld + (1 / min_drag) * inv_min_drag_scaling


def compound_score(max_lift,
                   min_drag,
                   max_lift_to_drag,
                   max_lift_scaling=30.,
                   inv_min_drag_scaling=0.3,
                   max_lift_to_drag_scaling=1.,
                   max_lift_weight=1.,
                   min_drag_weight=1.,
                   max_lift_to_drag_weight=1.):
    r"""Compute a score by blending different foil characteristics.
    Scaling brings the different values(max lift, min drag, max l/d)
    to the same range.
    Weights express the relative importance of each value
    (max lift, min drag, max l/d) for the intended application

    Parameters
    ----------
    max_lift
    min_drag
    max_lift_to_drag
    max_lift_scaling : float, optional
        multiplier of maximum lift
    inv_min_drag_scaling : float, optional
        multiplier of the inverse of minimum drag
    max_lift_to_drag_scaling : float, optional
        multiplier of the maximum lift to drag
    max_lift_weight : float, optional
        weight of max lift in the scoring logic
    min_drag_weight : float, optional
        weight of min drag in the scoring logic
    max_lift_to_drag_weight : float, optional
        weight of max L/D in the scoring logic
    """
    # logger.debug("max lift : %f" % max_lift)
    # logger.debug("max l/d : %f" % max_lift_to_drag)
    # logger.debug("min drag : %f" % min_drag)
    max_lift_score = max_lift_scaling * max_lift
    min_drag_score = inv_min_drag_scaling * (1. / min_drag)
    max_lift_to_drag_score = max_lift_to_drag_scaling * max_lift_to_drag

    score = ((max_lift_weight * max_lift_score +
             min_drag_weight * min_drag_score +
             max_lift_to_drag_weight * max_lift_to_drag_score) /
             (max_lift_weight + min_drag_weight + max_lift_to_drag_weight))

    return score
