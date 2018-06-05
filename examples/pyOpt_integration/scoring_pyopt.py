from functools import partial, update_wrapper

from pyOpt.optimization import Optimization
from pyOpt.pyALPSO.pyALPSO import ALPSO

from corelib.core.files import p_

from foilix.optimization.scoring import YachtAppendageNurbsSectionScorer


def wrapped_partial(func, *args, **kwargs):
    r"""Preserve the __name__ of the wrapped function"""
    partial_func = partial(func, *args, **kwargs)
    update_wrapper(partial_func, func)
    return partial_func


def objfunc_(x,
             angles_of_attack,
             aoa_ld, reynolds,
             ncrits,
             iterlim,
             inv_min_drag_scaling=0.3):
    r"""Objective function with explicit context"""
    try:
        scorer = YachtAppendageNurbsSectionScorer(angles_of_attack,
                                                  aoa_ld,
                                                  reynolds,
                                                  ncrits,
                                                  iterlim,
                                                  inv_min_drag_scaling)
        score = scorer.score(x)
        fail = 0
    except Exception:  # intentionally wide clause
        score = None
        fail = 1
    return score, [], fail


def create_objective_func(angles_of_attack,
                          aoa_ld,
                          reynolds,
                          ncrits,
                          iterlim,
                          inv_min_drag_scaling=0.3):
    r"""Create an objective function with embedded context"""
    return wrapped_partial(objfunc_,
                           angles_of_attack=angles_of_attack,
                           aoa_ld=aoa_ld,
                           reynolds=reynolds,
                           ncrits=ncrits,
                           iterlim=iterlim,
                           inv_min_drag_scaling=inv_min_drag_scaling)


objfunc = create_objective_func(angles_of_attack=[0, 10, 1],
                                aoa_ld=[3, 4, 5],
                                reynolds=[1e4, 2e4],
                                ncrits=[1, 2],
                                iterlim=200,
                                inv_min_drag_scaling=0.3)

opt_prob = Optimization('G08 Global Constrained Problem', objfunc)
opt_prob.addVar('x1', 'c', lower=0.0, upper=1, value=1.0)
opt_prob.addVar('x2', 'c', lower=0.0, upper=1, value=1.0)
opt_prob.addVar('x3', 'c', lower=0.0, upper=1, value=1.0)
opt_prob.addObj('f')

# Solve Problem (No-Parallelization)
print("---- No parallelization ----")
print(opt_prob)
alpso_none = ALPSO()
alpso_none.setOption('fileout', 1)
alpso_none.setOption('filename', p_(__file__, "ALPSO.out"))

alpso_none(opt_prob)

print(opt_prob.solution(0))

opt_prob.write2file(outfile=p_(__file__, 'opt_prob.log'),
                    disp_sols=True,
                    solutions=[0])
