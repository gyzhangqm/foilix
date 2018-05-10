# coding: utf-8

r"""This file contains the problem definition for a 2D section
optimization case"""

from os.path import join, dirname

# PSO parameters
nb_iterations = 12
swarm_size = 12
# Particle velocity scaling factor
omega = -0.2
# Scaling factor to search away from the particle's best known position
phi_p = 0.0
# Scaling factor to search away from the swarm's best known position
phi_g = 2.8

# define ranges of use
aoa_spec = (0., 10., 1.)
reynolds_number = [1.5e4, 3e4, 4.5e4, 6e4]
ncrits = [2.5, 3.]

# define scoring of characteristics for application : weights, scaling
aoa_ld = [3., 4., 5.]  # angles of attack where lift to drag should be evaluated
inv_min_drag_scaling = 0.25

# constraints : the following values will be added and substracted from the
# starting solution
# (i.e. parsec foil that mimics the best foils from db digging)
thickness_plus_minus = 0.01
max_thickness_x_plus_minus = .1
curvature_plus_minus = 1
le_radius_plus_minus = 0.004
te_angle_plus_minus = 4.

# db digging results file name
db_digging_filename = join(dirname(__file__), "db_digging.csv")

# Initial parameters file
initial_parsec_foil_params_filename = join(dirname(__file__),
                                           "initial_parsec_foil_params.data")

# save global best file name
save_global_best_file = join(dirname(__file__), "global_best.data")

# global best dat file
global_best_dat_file = join(dirname(__file__), "global_best.dat")

# TODO : check the reynolds, ncrits and angles are in the database
