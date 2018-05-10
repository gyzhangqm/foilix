#!/usr/bin/python
# coding: utf-8

r"""Test of Particle Swarm Optimization algorithm,
using the Rastrigin function."""

from __future__ import division, print_function

import logging
from copy import copy

import matplotlib.pyplot as plt
import numpy as np

from foilix.optimization.pso import Particle

logger = logging.getLogger(__name__)


def rastrigin_nd_randnone(*xi):
    r"""Simulates airfoils that don't converge 
    in Xfoil by randomly returning None"""
    # Return None 20% of the time
    if np.random.rand() > .8:
        return None
    else:
        return rastrigin_nd(*xi)


def rastrigin_nd(*xi):
    r"""n-dimensional rastrigin function. Every argument should be a 
    single value or meshgrid, and is another dimension.
    """
    return 10 * len(xi) + np.sum(a**2 - (10 * np.cos(2 * np.pi * a)) for a in xi)


def rastrigin_example():
    r"""Runs the example"""
    # Parameters for 5 iterations, 1,000 function evaluations from:
    # http://hvass-labs.org/people/magnus/publications/pedersen10good-pso.pdf
    iterations, S, omega, phi_g, phi_p = 20, 23, -0.3328, 2.8446, 0
    global_bestscore = None
    global_bestpos = None

    constraints = np.array(((-5, 5), (-5, 5)))

    x, y = np.meshgrid(np.arange(*np.append(constraints[0], .05)),
                       np.arange(*np.append(constraints[1], .05)))
    plt.title("Rastrigin function")
    plt.contourf(x, y, rastrigin_nd(x, y), cmap=plt.cm.coolwarm)
    plt.ion()
    # plt.axis(constraints.flatten())

    # Constructing a particle automatically initializes position and speed
    particles = [Particle(constraints) for i in range(0, S)]

    # Python 3 range is Python 2's xrange
    # (minimal impact of using range in Python 2)
    for n in range(iterations + 1):
        print("\nIteration {}\n".format(n))
        for particle in particles:
            # Keep scoring until converged
            score = None
            while not score:
                # Update particle's velocity and position, after first loop
                if n > 0:
                    particle.update(global_bestpos, omega, phi_p, phi_g)
                    # particle.APSO(global_bestpos, .5, .5)
                # Score
                score = rastrigin_nd_randnone(*particle.pts)
                if score is None:
                    print("Not converged")
                    if n == 0:
                        print("First loop so randomizing particle")
                        particle.randomize()

            # plt.plot(particle.pts[0], particle.pts[1], 'yx')

            if score < particle.bestscore:
                particle.new_best(score)
                style, txt = 'bo', 'particle best'
                if not global_bestscore or score < global_bestscore:
                    global_bestscore = score
                    # Copy to avoid globaL_bestpos becoming reference to array
                    global_bestpos = copy(particle.pts)
                    style, txt = 'ro', 'global best'
                print("Plotting {} ({}, {})".format(txt, *particle.pts))
                plt.pause(0.00001)
                plt.plot(particle.pts[0], particle.pts[1], style)

    print("Global best score: ",
          global_bestscore,
          "Global best pos: ",
          global_bestpos)
    plt.plot(global_bestpos[0], global_bestpos[1], 'yx', markersize=12)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s :: %(levelname)6s :: %(module)20s '
                               ':: %(lineno)3d :: %(message)s')
    rastrigin_example()
