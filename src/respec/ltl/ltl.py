#!/usr/bin/env python

"""
Boolean operators and the 'next' LTL operator.

The remaining LTL operators are not (currently) needed because 
the specification module is using the .structuredslugs format.
"""
		
def conj(terms):
	if len(terms) > 1:
		return paren(" & ".join(terms))
	else:
		return terms[0]

def disj(terms):
	if len(terms) > 1:
		return paren(" | ".join(terms))
	else:
		return terms[0]

def neg(term):
	return "! " + term

def next(term):
	if term[0] == '(' and term[-1] == ')':
		return 'next' + term
	else:
		return 'next' + paren(term)

def implication(left_hand_side, right_hand_side):
	return left_hand_side + " -> " + right_hand_side

def iff(left_hand_side, right_hand_side):
	return left_hand_side + " <-> " + right_hand_side

def paren(term):
	return "(" + term + ")"
