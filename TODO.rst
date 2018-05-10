Some tests do not pass anymore

Data files (+ RBF interp instead of DB)

Script the DB creation (bat and/or sh)

Replace doctests (e.g. parsec) by real tests

Try with xfoil on Linux. If it works -> Dockerfile


More FP + More modular/abstract

Understand why some errors happen (e.g. TypeError for gf_0001.dat)

Polar taking Cl instead of aoas as input
    It is the same in the end as drag at Cl==0.5 could be obtained by interpolation of Cd = f(Cl)

Interpolating with PChip is not useful to determines maximums and minimums dur to the nature of PChip (polar.py)
    The interpolation slows down db digging  lot
    Have an option to determine which interpolation should be used (linear will do as well as PChip for mins and maxs but faster)

More points would be required in db for more precision (db digging and optimization have to be done on the same angles)
    The max L/D and max lift would get more realistic instead of being limited to definition angles
    (side effect of using PChip interpolation in Polar)

Check for is_symmetrical instead of is_symmetrical() in every file

Drag logic for yachts: min_drag + avg drag at a set of Cl ??

Some calculation stall at 11 degrees when feeding db -> try to timeout find_coefficients
ys900 not computed -> why

Check optimization foil robustness outside of optimization domain -> how?

Xfoil
-----

Influence of the number of panels

UI
--

Add sorting and foil thumbnails to NewLoggingFrame

Code
----

optimize with opemMDAO or pyopt, so that more tha a single strategy can be used

Write a test pour exclusion formes + larges que max_thickness dans is_valid() de parsec.py

better setup.py

github repo tags in sync with what is recommended in best practises


Optimization strategies
-----------------------

Optimal parameters selection for PSO (cf. http://hvass-labs.org/people/magnus/publications/pedersen10good-pso.pdf)

Study OpenMDAO
https://github.com/OpenMDAO-Plugins/pyopt_driver/blob/master/docs/usage.rst
