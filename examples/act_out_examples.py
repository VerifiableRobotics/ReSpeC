from respec.formula.activation_outcomes import *

ts = {'r1': ['r1', 'r2'],
      'r2': ['r2'],
      'r3': ['r3', 'r1']}

ts_formula = TransitionRelationFormula(ts)

print 'Transition System:'
print ts

print 'LTL Formulas:'

for formula in ts_formula.formulas:
	print formula
