#!/usr/bin/env python
# coding: utf-8

r"""OpenMDAO foil component

WORK IN PROGRESS

"""

from __future__ import print_function

from openmdao.api import IndepVarComp, Component, Problem, Group, \
    ScipyOptimizer, ExecComp


class Foil(Component):
    r"""Define a foil as an OpenMDAO Component
    using a PARSEC parameterization"""
    def __init__(self):
        super(ParsecFoil, self).__init__()
        self.add_param('leading_edge_radius')
        self.add_param('max_thickness')
        self.add_param('max_thickness_y')
        self.add_param('curvature_at_max_thickness')
        self.add_param('trailing_edge_angle')

        # default value required if not connected but promoted
        self.add_param('Rns', val=[1, 2])

        # .....
        # how to add aoas, reynolds, ncrits, iterlim? scoring settings?

        self.add_output('max_cl', shape=1)
        self.add_output('angle_at_max_cl', shape=1)
        self.add_output('max_lift_to_drag', shape=1)
        self.add_output('angle_at_max_lift_to_drag', shape=1)
        self.add_output('min_cd', shape=1)
        self.add_output('angle_at_min_cd', shape=1)

        # Finite difference because not differentiable
        self.deriv_options['type'] = 'fd'

    def solve_nonlinear(self, params, unknowns, resids):
        print("solve_nonlinear called")
        # create foil
        # call x foil
        ler = params["leading_edge_radius"]
        mt = params["max_thickness"]
        rns = params["Rns"]
        unknowns['max_cl'] = (ler + mt) * rns[0]

top = Problem()
root = top.root = Group()
root.add("p_leading_edge_radius", IndepVarComp("leading_edge_radius", 0.2))
root.add("p_max_thickness", IndepVarComp("max_thickness", 0.19))
root.add("p_max_thickness_y", IndepVarComp("max_thickness_y", 0.2))
root.add("p_curvature_at_max_thickness",
         IndepVarComp("curvature_at_max_thickness", 0.02))
root.add("p_trailing_edge_angle", IndepVarComp("trailing_edge_angle", 5.))

root.add("p", ParsecFoil(), promotes=["Rns"])

# Constraint Equation
root.add('con', ExecComp('c = leading_edge_radius - max_thickness'))


root.connect('p_leading_edge_radius.leading_edge_radius',
             'p.leading_edge_radius')
root.connect('p_max_thickness.max_thickness', 'p.max_thickness')
root.connect('p_max_thickness_y.max_thickness_y', 'p.max_thickness_y')
root.connect('p_curvature_at_max_thickness.curvature_at_max_thickness',
             'p.curvature_at_max_thickness')
root.connect('p_trailing_edge_angle.trailing_edge_angle',
             'p.trailing_edge_angle')

root.connect('p.leading_edge_radius', 'con.leading_edge_radius')
root.connect('p.max_thickness', 'con.max_thickness')

# top.driver = Driver()
top.driver = ScipyOptimizer()
top.driver.options["optimizer"] = 'SLSQP'
top.driver.options["maxiter"] = 1000
top.driver.options["tol"] = 1e-6

top.driver.add_desvar("p_leading_edge_radius.leading_edge_radius",
                      lower=0.01,
                      upper=0.1)
top.driver.add_desvar("p_max_thickness.max_thickness", lower=0.05, upper=0.2)
top.driver.add_objective('p.max_cl')  # Any unknown can be used as the objective

top.driver.add_constraint('con.c', lower=0., upper=0.04)


top.setup()
top["Rns"] = [1e5, 1e6]
top.run()

print(top['p.max_cl'])
print(top['p.leading_edge_radius'])
print(top['p.max_thickness'])
print(top['p.leading_edge_radius'] - top['p.max_thickness'])

print(0. <= top['p.leading_edge_radius'] - top['p.max_thickness'] <= 0.04)
