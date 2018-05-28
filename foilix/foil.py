# coding: utf-8

r"""Foil model (name and list of points) and properties"""

import os.path
import re
import logging
from math import sqrt

logger = logging.getLogger(__name__)


class Foil(object):
    r"""Foil representation as a name and a list of points

    Parameters
    ----------
    name : str
        The name given to the foil
    points : tuple(tuple(float, float))
        List of point coordinates

    """
    def __init__(self, name, points):
        self.name = name
        self.points = points

    @classmethod
    def from_dat_file(cls, filepath):
        r"""Construct a Foil from a path to a dat file

        Selig and Lednicer formats are handled transparently,
        i.e. the original order present in the dat file is preserved
        Selig:
        Xte --(upper)--> Xle --(lower)--> Xte
        Lednicer
        Xle --(upper)--> Xte  Xle --(lower)--> Xte

        Parameters
        ----------
        filepath : str

        """
        # TODO : handle funny formats by reordering
        #        positive ys by descending x, negative ys by ascending x
        #        then join the 2 lists
        #        only works for symmetrical foils
        #        (where is the leading edge on an unsymmetrical foil anyway?)
        name = os.path.splitext(os.path.basename(filepath))[0]

        points = list()

        import sys

        mode = 'rb' if sys.version_info[0] >= 3 else 'r'

        with open(filepath, mode) as f:
            for line in f.readlines():
                regex = b'\S+' if sys.version_info[0] >= 3 else r'\S+'
                line_items = re.findall(regex, line)
                try:
                    x, y = float(line_items[0]), float(line_items[1])
                    # see header of bqm34.dat or clarky.dat to see
                    # why <= 1 is required in the next if statement
                    if x <= 1. and y <= 1:
                        points.append((x, y))
                except (ValueError, IndexError):
                    pass  # This is normal behavior, happens on header lines
                    # print("Wrong data or header, skipping it")
        return cls(name, tuple(points))

    def is_symmetrical(self, tolerance=1.2e-5):
        r"""Test the symmetry of the foil

        Parameters
        ----------
        tolerance : float (optional, default is 1.2e-5)

        Returns
        -------
        bool : True if symmetrical, False otherwise

        """
        # some foils are unsymmetrical (near trailing edge e.g. sc20402.dat
        # or in the middle e.g. stcyr171.dat)
        # but are considered symmetrical by this function
        # -> test on the whole array

        upper_ys = [y for _, y in self.points if y > 0.]
        lower_ys = [abs(y) for _, y in self.points if y < 0.]

        # some foils only have positive coordinates
        if len(upper_ys) == 0 or len(lower_ys) == 0:
            logger.debug("%s is not symmetrical - all ys are positive" %
                         self.name)
            return False

        if len(upper_ys) != len(lower_ys):
            logger.debug("%s is not symmetrical - different number of positive "
                         "and negative points" % self.name)
            return False

        # basic condition for symmetry, look no further if not the case
        if not (max(upper_ys) - tolerance <= max(lower_ys) <= max(upper_ys) + tolerance):
            logger.debug("%s is not symmetrical - maximums do not match" %
                         self.name)
            return False

        # some foils are defined 1 -> 0 -> 1 and others are
        #                                                 defined 0 -> 1 0 -> 1
        # consider both cases
        lower_ys_reversed = list(reversed([abs(p[1]) for p in self.points if p[1] < 0.]))
        for y_u, y_l, y_l_reversed in zip(upper_ys, lower_ys, lower_ys_reversed):
            # add an 1e-6 tolerance for repaneled airfoils
            if not(y_l - tolerance <= y_u <= y_l + tolerance) and \
                    not(y_l_reversed - tolerance <= y_u <= y_l_reversed + tolerance):
                logger.debug("%s is not symmetrical - at least a point is not "
                             "symmetrical" % self.name)
                logger.debug("y_l : %s" % str(y_l))
                logger.debug("y_u : %s" % str(y_u))
                logger.debug("y_l_reversed : %s" % str(y_l_reversed))
                logger.debug("tolerance : %s" % str(tolerance))
                return False

        return True

    @property
    def y_spread(self):
        r"""Foil y spread (maximum y - minimum y)

        This the foil thickness if the foil is symmetrical

        Returns
        -------
        float : The y spread of the foil

        """
        return max([y for _, y in self.points]) - min([y for _, y in self.points])

    @property
    def max_y_x(self):
        r"""Foil x position of maximum y

        This the x position of maximum thickness if the foil is symmetrical

        Returns
        -------
        float : The x position of max y

        """
        ys = [y for _, y in self.points]
        y_max = max(ys)
        return self.points[ys.index(y_max)][0]

    @property
    def min_y_x(self):
        r"""Foil x position of minimum y

        This the x position of maximum thickness if the foil is symmetrical

        Returns
        -------
        float : The x position of min y

        """
        ys = [y for _, y in self.points]
        y_min = min(ys)
        return self.points[ys.index(y_min)][0]

    @property
    def pseudo_leading_edge_radius(self):
        r"""Estimation of the leading edge radius using points
        around leading edge

        Returns
        -------
        radius : float
            Leading edge radius estimate

        """
        # TODO : the estimate is based on an odd number of points
        #            -> what happens for even numbers?
        # TODO : Value about 3 times higher than theory for naca0006 -> why?
        # TODO : Lednicer format correctly handled ??
        # from
        #   https://fr.mathworks.com/matlabcentral/newsreader/view_thread/128429
        try:
            mid_point_index = int(len(self.points) / 2)
            x2, y2 = self.points[mid_point_index]
            x1, y1 = self.points[mid_point_index - 1]
            x3, y3 = self.points[mid_point_index + 1]

            # The three sides
            a = sqrt((x1 - x2)**2 + (y1 - y2)**2)
            b = sqrt((x2 - x3)**2 + (y2 - y3)**2)
            c = sqrt((x3 - x1)**2 + (y3 - y1)**2)
            s = (a + b + c) / 2
            A = sqrt(s * (s - a) * (s - b) * (s - c))  # Area of triangle
            R = a * b * c / (4 * A)  # Radius of circumscribing circle
            return R
        except ZeroDivisionError:
            return -1

    @property
    def has_closed_te(self):
        r"""Is the trailing edge closed?

        Returns
        -------
        bool

        """
        if self.points[0][1] == self.points[-1][1] == 0.:
            return True
        else:
            return False
