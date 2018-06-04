# coding: utf-8

r"""Pso algorithm"""

from __future__ import division, print_function

# import os
import threading
import copy
import logging

import numpy as np
# from numpy.random import normal, uniform
#  Import N(mu, sigma) and U[0,1) function

from foilix.ui.observer import Observable

logger = logging.getLogger(__name__)


class Particle(object):
    r"""class to handle Particle Swarm Optimization.
    Its abstraction level is such that it should be similar to
    thinking about the algorithm.

    A particle is an array of constrained numbers.
    The constraint array c is organized as [[low,high],[low,high]].

    References
    ----------
    Great paper on parameter selection:
    http://hvass-labs.org/people/magnus/publications/pedersen10good-pso.pdf

    http://arxiv.org/pdf/1203.6577.pdf

    """

    def __init__(self, constraints):
        logger.debug("Instantiating particle")
        self.bestscore = None
        self.bestpts = None
        self.oldpts = None
        self.oldspeeds = None

        self.constraints = constraints
        self.pts = np.zeros(len(constraints), dtype="float")
        self.speeds = np.zeros(len(constraints), dtype="float")

        self.randomize()  # Randomize positions and speeds
        self.new_best(float('inf'))  # Set current point as best

    def new_best(self, score):
        r"""Stores new personal best score and position (pts).

        Parameters
        ----------
        score : float
            The new best score

        """
        logger.debug("Setting new best for particle %s" % str(id(self)))
        self.bestscore = score
        self.bestpts = self.pts

    def randomize(self):
        r"""Randomize with uniform distribution within bounds.
        Using numpy.random.uniform"""

        # Iterate over self.pts
        for i, (lowerbound, upperbound) in enumerate(self.constraints):
            # Draw samples from a uniform distribution.
            # Samples uniformly distributed over the half-open
            # interval [low, high) (includes low, but excludes high)
            # In other words, any value within the given interval is
            # equally likely to be drawn by uniform.
            # Note: uniform() returns a single value
            self.pts[i] = np.random.uniform(lowerbound, upperbound)
            absrange = abs(upperbound-lowerbound)
            self.speeds[i] = np.random.uniform(-absrange, absrange)

    def update(self, global_best, omega, phi_p, phi_g):
        r"""Update velocity and position

        Parameters
        ----------
        global_best : N (same dimension as constraints) dimensional array
            The global best found by the swarm
        omega :float
            Particle velocity scaling factor
        phi_p : float
            Scaling factor to search away from the particle’s
            best known position
        phi_g : float
            Scaling factor to search away from the swarm’s best known position
        """
        logger.debug("Update particle %s" % str(id(self)))
        # Copy to prevent self.oldpts becoming reference to self.pts array
        self.oldpts = copy.copy(self.pts)

        # Copy to prevent self.oldspeeds becoming reference to self.speeds array
        self.oldspeeds = copy.copy(self.speeds)

        r_p, r_g = np.random.uniform(0, 1), np.random.uniform(0, 1)
        # v_i,d <- omega*v_i,d + theta_p*r_p*(p_i,d-x_i,d) +
        #                                                theta_g*r_g*(g_d-x_i,d)
        self.speeds = (omega * self.speeds + phi_p * r_p *
                       (self.bestpts - self.pts)
                       + phi_g * r_g * (global_best - self.pts))
        self._boundspeeds()
        self.pts += self.speeds
        self._boundpts()

    def rewind(self):
        r"""Go back to previous velocity and position"""
        # Copy to prevent self.pts becoming reference to self.oldpts array
        try:
            self.pts = copy.copy(self.oldpts)
            self.speeds = copy.copy(self.oldspeeds)
        except NameError:
            raise Warning("Update was never called, so no rewind possible.")

    def _boundpts(self):
        r"""Restrict points to lowerbound < x < upperbound"""
        for i, (lowerbound, upperbound) in enumerate(self.constraints):
            pt = self.pts[i]
            if pt < lowerbound:
                self.pts[i] = lowerbound
            if pt > upperbound:
                self.pts[i] = upperbound

    def _boundspeeds(self):
        r"""Restrict speeds to -range < v < range"""
        for i, (lowerbound, upperbound) in enumerate(self.constraints):
            spd = self.speeds[i]
            absrange = abs(upperbound - lowerbound)
            if spd < -absrange:
                self.pts[i] = -absrange
            if spd > absrange:
                self.pts[i] = absrange

    def __str__(self):
        r"""Print values of Particle."""
        return "Constraints: " + self.constraints.__str__() + \
               "\nValues: " + self.pts.__str__()

    def APSO(self, global_best, B, a):
        r"""A simplified way of PSO, with no velocity,
                                             updating the particle in one step.
        http://arxiv.org/pdf/1203.6577.pdf
        Typically, a = 0.1L ~ 0.5L where L is the scale of each variable,
        while B = 0.1 ~ 0.7 is sufficient for most applications.

        Parameters
        ----------
        global_best
        B
        a

        """
        self.oldpts = copy.copy(self.pts)
        self.oldspeeds = copy.copy(self.speeds)
        for i, pt in enumerate(self.pts):
            mu, sigma = 0, 1
            e = np.random.normal(mu, sigma)
            c = self.constraints[i]
            L = abs(c[1] - c[0])
            self.pts[i] = (1 - B) * L * pt + B * L * global_best[i] + a * L * e
        self._boundpts()


class PsoAlgorithm(Observable, threading.Thread):
    r"""Generic PSO algorithm

    Parameters
    ----------
    constraints : list[2-tuple(float)]
        List of tuples representing the min and max acceptable
        values for each point
    scoring_object : subclass of foilix.optimization_algorithms.scoring.Scorer
        The object that has a score() function to define the score
        corresponding to the pts
    iterations : int
        The number of iterations for the swarm to search
    S: int
        The number of particles in the swarm
    omega :float
        Particle velocity scaling factor
    phi_p : float
        Scaling factor to search away from the particle’s best known position
    phi_g : float
        Scaling factor to search away from the swarm’s best known position
    save_global_best: str or None
        Path to save the global best of the optimization

    References
    ----------
    Good parameters at:  http://hvass-labs.org/people/magnus/publications/
                                                          pedersen10good-pso.pdf

    """
    def __init__(self,
                 constraints,
                 scoring_object,
                 iterations=12,
                 S=12,
                 omega=-0.2,
                 phi_p=0.0,
                 phi_g=2.8,
                 save_global_best=None):
        super(PsoAlgorithm, self).__init__()
        threading.Thread.__init__(self)
        # if thickness < 0.0 or thickness > 0.3 or type(thickness) is not float:
        #     raise ValueError("thickness should be a strictly positive float,
        #                       smaller than 0.3")
        # self.thickness = thickness
        # self.operating_range = operating_range
        self.constraints = constraints
        self.iterations = iterations
        self.S = S
        self.omega = omega
        self.phi_p = phi_p
        self.phi_g = phi_g
        self.save_global_best = save_global_best

        self.scoring_object = scoring_object
        # self.scoring_parameters = scoring_parameters

        # self._global_bestscore, self._global_bestpos, self._global_bestairfoil
        #                                                     = None, None, None
        self._global_bestscore, self._global_bestpos = None, None

        self.particles = [Particle(self.constraints) for _ in range(0, self.S)]

        self._scores_y = []

    @property
    def global_bestscore(self):
        return self._global_bestscore

    @global_bestscore.setter
    def global_bestscore(self, value):
        self._global_bestscore = value

    @property
    def global_bestpos(self):
        return self._global_bestpos

    @global_bestpos.setter
    def global_bestpos(self, value):
        self._global_bestpos = value

    # @property
    # def global_bestairfoil(self):
    #     return self._global_bestairfoil
    #
    # @global_bestairfoil.setter
    # def global_bestairfoil(self, value):
    #     self._global_bestairfoil = value

    @property
    def scores_y(self):
        return self._scores_y

    @scores_y.setter
    def scores_y(self, value):
        self._scores_y = value

    def run(self):
        r"""Run the PSO algorithm"""
        self.optimize()

    def optimize(self):
        r"""Optimization logic"""
        logger.info("Starting optimization ....\n")
        for n in range(self.iterations + 1):
            logger.info("Iteration {}\n".format(n))
            for i_par, particle in enumerate(self.particles):
                # repeated for easier log reading
                logger.info("Iteration {}".format(n))

                logger.info("Particle {}".format(i_par))
                logger.info(particle.pts.__str__())

                score = None
                while not score:  # Keep scoring until converged
                    # Update particle's velocity and position, if global best
                    if self.global_bestscore:
                        logger.info("Update particle")
                        particle.update(self.global_bestpos,
                                        self.omega,
                                        self.phi_p,
                                        self.phi_g)
                    logger.info(particle.pts.__str__())
                    # None if not converged
                    # airfoil = self.construct_airfoil(*particle.pts)
                    score = self.scoring_object.score(particle.pts)
                    logger.info("Score : %.5f (%.3f)"
                                % (score if score is not None else float('nan'),
                                   1.0 / score if score is not None else float('nan')))

                    # 1st display from top

                    if score is not None:
                        self.notify_observers("current_particle",
                                              n,
                                              i_par,
                                              particle.pts,
                                              score,
                                              self.scoring_object.parameterization_type)

                    if not score and (not self.global_bestscore or n == 0):
                        logger.info("Not converged, no global best, "
                                    "or first round. Randomizing particle.")
                        particle.randomize()
                        logger.info(particle.pts.__str__())
                    elif not score:
                        logger.info("Not converged, there is a global best. "
                                    "Randomizing.")
                        particle.randomize()
                        logger.info(particle.pts.__str__())
                # end while not score

                # lower score is better !!
                if not particle.bestscore or score < particle.bestscore:
                    particle.new_best(score)
                #
                #     if score is not None:
                #         self.notify_observers("particle_best",
                #                               n,
                #                               i_par,
                #                               particle.pts,
                #                               score,
                # self.scoring_object.parameterization_type)
                #     logger.info("Found particle best, score {}".format(score))

                # lower score is better !!
                if not self.global_bestscore or score < self.global_bestscore:
                    self.global_bestscore = score
                    # Copy to avoid globaL_bestpos becoming reference to array
                    self.global_bestpos = copy.copy(particle.pts)

                    # 3rd display from top
                    if score is not None:
                        self.notify_observers("global_best",
                                              n,
                                              i_par,
                                              particle.pts,
                                              score,
                                              self.scoring_object.parameterization_type)

                    logger.info("Found global best, score {}".format(score))
                    # self.global_bestairfoil = airfoil

            self.scores_y.append(self.global_bestscore)

        # end for n in range(self.parameters.iterations + 1)

        print("score = ",
              self.global_bestscore,
              ", pos = ",
              self.global_bestpos.__repr__())

        if self.save_global_best is not None:
            with open(self.save_global_best, "w") as f:
                f.write(str(self.global_bestscore) + "\n")
                f.write(str(1./self.global_bestscore) + "\n")
                f.write("--\n")
                for value in self.global_bestpos:
                    f.write(str(value) + "\n")
                # f.write(str(self.global_bestpos.__repr__()) + "\n")
