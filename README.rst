Foilix
======

.. image:: https://travis-ci.org/guillaume-florent/foilix.svg?branch=master
    :target: https://travis-ci.org/guillaume-florent/foilix
.. image:: https://api.codacy.com/project/badge/Grade/5af705e42e5749a8b86faa0bf5c69a4e
    :target: https://www.codacy.com/app/guillaume-florent/foilix?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=guillaume-florent/foilix&amp;utm_campaign=Badge_Grade

**foilix** is a set of python programs to analyze and optimize 2D foil sections. **foilix** uses Xfoil_ to determine the 2D foil section behaviour for a specific operating range.

.. _Xfoil: http://web.mit.edu/drela/Public/web/xfoil/

Goals:

- assess the performance of a 2D foil section for a specific operating range
- optimize a parametric 2D foil section for a specific operating range
- score a 2D foil section by using weighting factors for its main characteristics (L max; L/D max, min drag)


For some reason, the optimization algorithms run much faster in Python 2. An investigation has yet to be done.

Use the Docker containers to use the best Python version for each *foilix_opt_step<n>_<desc>* optimization step on a case under $HOME (common volume)!

PARSEC and NURBS parameterizations can both be used to optimize the same case


Xfoil
-----

Xfoil_ is an interactive program for the design and analysis of subsonic isolated airfoils.
Given the coordinates specifying the shape of a 2D airfoil, Reynolds and Mach numbers, XFOIL can calculate the
pressure distribution on the airfoil and hence lift and drag characteristics.
The program also allows inverse design - it will vary an airfoil shape to achieve the desired parameters.
It is released under the GNU GPL.

Particle Swarm Optimization
---------------------------

PSO is an optimization technique inspired by a flock of birds searching for food.
It is relatively simple, doesn't concern itself with gradients, and often outperforms more complex techniques like genetic algorithms.

It can easily be applied to airfoils, simply by translating the list of constrained numbers into an airfoil,
then scoring the airfoil using the **xfoil.py** module to get lift, drag, moment or anything else at a specified Re and alpha or Cl.
