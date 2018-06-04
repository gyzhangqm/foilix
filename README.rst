Foilix
======

.. image:: https://travis-ci.org/floatingpointstack/foilix.svg
    :alt: build status
.. image:: https://coveralls.io/repos/floatingpointstack/foilix/badge.svg?branch=master&service=github
    :alt: code coverage
.. image:: http://img.shields.io/badge/license-GPL v3-blue.svg
    :alt: GPL v3

**foilix** is a set of python programs to analyze and optimize 2D foil sections. **foilix** uses Xfoil_ to determine the 2D foil section behaviour for a specific operating range.

.. _Xfoil: http://web.mit.edu/drela/Public/web/xfoil/

Goals:

- assess the performance of a 2D foil section for a specific operating range
- optimize a parametric 2D foil section for a specific operating range
- score a 2D foil section by using weighting factors for its main characteristics (L max; L/D max, min drag)


The bin folder should be in PATH (either manually by altering bashrc or via a conda install (to be created)

Getting started
---------------

see section_analysis_example.py in examples/foil_section_analysis
see pso_example.py in examples/optimization to see how to optimize a section

Python
------

Recommended Python version is 2.7.*

For some reason, the optimization algorithms run much faster in Python 2. An investigation has yet to be done.

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
