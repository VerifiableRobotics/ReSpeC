#!/usr/bin/env python

from ..ltl import ltl as LTL

"""
Formulas for the GR(1) fragment of Linear Temporal Logic

This module contains two main classes:
  * GR1Formula for vanilla GR(1) formulas
  * FastSlowFormula for extended GR(1) formulas following the paradigm 
    in Vasumathi Raman and Hadas Kress-Gazit (ICRA 2013)

The LTL syntax used is that of .structuredslugs, 
which is meant for use with the SLUGS synthesis tool.

"""

class GR1Formula(object):
	"""

	Arguments:
	  env_props (list of str)	Environment propositions (strings)
	  sys_props (list of str)	System propositions (strings)
	  ts 		(dict of str)	Transition system, TS (e.g. workspace topology)
	  							Implicitly contains propositions in the keys.

	Attributes:
	  formula 	(list of str)	Formulas whose conjunction makes up a type
	  							of GR(1) subformulas (e.g. fairness conditions)
	  type		(str)			GR(1) subformula type (sys_init, env_init,
	  							sys_trans, env_trans, sys_liveness,
	  							env_liveness)

	Raises:
	  ValueError:				When a proposition is neither a system nor
	  							an environment proposition

	"""
	
	def __init__(self, env_props = [], sys_props = [], ts = {}):
		#FIX: TS should be an argument of a subclass, not base class
		self.sys_props = sys_props
		self.env_props = env_props
		self.ts = ts

		self._add_props_from_ts()

		# The formulas and their subfomrula type is set for
		# classes (subformulas) that inherit from GR1Formula
		self.formulas = list()
		self.type = str()
		#TODO: Make formulas a property. Setter would work with
		# either a single formula or a list of formulas.

	
	# =====================================================
	# System and environment initial conditions
	# =====================================================

	def gen_sys_init_from_prop_assignment(self, prop_assignment, props = "sys_props"):
		"""
		Set the given propositions to the desired truth value in the
		system initial conditions formula. Set all the others to False.
		"""
		
		sys_init = list()

		props_of_type = getattr(self, props)

		for prop in props_of_type:
			if prop in prop_assignment.keys():
				if prop_assignment[prop] is True:
					sys_init.append(prop)
				else:
					sys_init.append(LTL.neg(prop))
			else:
				sys_init.append(LTL.neg(prop))
		
		return sys_init

	def gen_env_init_from_prop_assignment(self, prop_assignment, props = "env_props"):
		"""
		Set the given propositions to the desired truth value in the
		environment initial conditions formula. Set all the others to False.
		"""
		
		env_init = list()

		props_of_type = getattr(self, props)

		for prop in props_of_type:
			if prop in prop_assignment.keys():
				if prop_assignment[prop]:
					env_init.append(prop)
				else:
					env_init.append(LTL.neg(prop))
			else:
				env_init.append(LTL.neg(prop))
		
		return env_init

	# =====================================================
	# System transition formulas (e.g., workspace topology)
	# =====================================================

	def gen_sys_trans_formulas(self, future = True):
		"""
		Generate system requirement formulas that
		encode the transition system (e.g. workspace topology).

		The transition system TS, is provided in the form of a dictionary.
		"""
		sys_trans_formulas = list()
		for prop in self.ts.keys():
			left_hand_side = prop
			right_hand_side = list()
			
			for adj_prop in self.ts[prop]:
				adj_phi_prop = self._gen_phi_prop(adj_prop)
				disjunct = LTL.next(adj_phi_prop) if future else adj_phi_prop
				right_hand_side.append(disjunct)

			right_hand_side = LTL.disj(right_hand_side)
			sys_trans_formulas.append(LTL.implication(left_hand_side,
													  right_hand_side))

		return sys_trans_formulas

	# =====================================================
	# Various formulas
	# =====================================================

	def gen_mutex_formulas(self, mutex_props, future):
		""" 
		Create a set of formulas that enforce mutual exclusion
		between the given propositions, see Eq. (1).

		The argument 'future' dictates whether the propositions will be
		primed (T) or not (F). Should be set to True in fast-slow formulas.
		"""

		mutex_formulas = list()

		for prop in mutex_props:
			other_props = [p for p in mutex_props if p != prop]
			negated_props = list()
			for prop_prime in other_props:
				if future:
					left_hand_side = LTL.next(prop)
					neg_prop = LTL.neg(LTL.next(prop_prime))
				else:
					left_hand_side = prop
					neg_prop = LTL.neg(prop_prime)
				negated_props.append(neg_prop)
			right_hand_side = LTL.conj(negated_props)
			
			mutex_formulas.append(LTL.iff(left_hand_side, right_hand_side))

		return mutex_formulas

	def gen_precondition_formula(self, action, preconditions):
		'''Conditions that have to hold for an action (prop) to be allowed.'''

		neg_preconditions = map(LTL.neg, preconditions)
		left_hand_side = LTL.disj(neg_preconditions)
		right_hand_side = LTL.neg(action)

		precondition_formula = LTL.implication(left_hand_side, right_hand_side)

		return precondition_formula

	def gen_success_condition(self, mem_props, success = 'finished'):
		'''
		Creates a formula that turns 'finshed' to True
		when all memory propositions corresponding to success have been set.'''

		conjunct = LTL.conj(mem_props)

		success_condition = LTL.iff(success, conjunct)

		return success_condition

	def gen_goal_memory_formula(self, goal):
		'''
		For a proposition corresponding to a desired objective, creates a memory
		proposition and formulas for remembering achievement of that objective.'''

		mem_prop = self.gen_memory_prop(goal)

		set_mem_formula = LTL.implication(goal, LTL.next(mem_prop))
		remembrance_formula = LTL.implication(mem_prop, LTL.next(mem_prop))
		precondition = LTL.conj([LTL.neg(mem_prop), LTL.neg(goal)])
		guard_formula = LTL.implication(precondition, LTL.next(LTL.neg(mem_prop)))

		goal_memory_formula = list([set_mem_formula, remembrance_formula, guard_formula])

		return mem_prop, goal_memory_formula

	def gen_memory_prop(self, prop):
		'''
		Creates a memory proposition from the given proposition
		and adds the memory proposition to the system propositions.'''

		mem_prop = prop + '_m'

		self.sys_props.append(mem_prop)

		return mem_prop

	# =====================================================
	# Various helper methods
	# =====================================================

	def _add_props_from_ts(self):
		"""Reads the items in the TS dictionary and adds them to the system propositions, if they are not already there."""

		props_to_add = self.ts.keys()
		for v in self.ts.values():
			for prop in v:
				props_to_add.append(prop)

		self.sys_props = list(set(self.sys_props + props_to_add))

	def _gen_phi_prop(self, prop):
		"""
		Generate (non-atomic) proposition of the form \phi_r,
		i.e., mutex version of \pi_r (where prop = \pi_r)
		"""
		
		props_in_phi = [prop] # Initialize with just pi_r

		other_props = self._get_other_trans_props(prop)
		for other_prop in other_props:
			props_in_phi.append(LTL.neg(other_prop)) # All pi_r' are negated

		phi_prop = LTL.conj(props_in_phi)

		return phi_prop

	def _get_other_trans_props(self, prop):
		"""For some proposition \pi_r, get all propositions \pi_r' such that r' =/= r."""
		
		if prop in self.sys_props:
			return [p for p in self.sys_props if p != prop]
		elif prop in self.env_props:
			return [p for p in self.env_props if p != prop]
		else:
			raise ValueError("Unknown type for proposition: %s" % prop)


class SimpleLivenessRequirementFormula(GR1Formula):
    """
    Generates a single liveness requirement that's either a conjunction
    or disjunction of the goals, depending on the flag. 
    """

    def __init__(self, goals, disjunction = False):
        super(SimpleLivenessRequirementFormula, self).__init__(
        												sys_props = goals)

        self.formulas = self._gen_liveness_formula(goals, disjunction)

        self.type = 'sys_liveness'

    def _gen_liveness_formula(self, goals, disjunction):
        
        liveness_formula = LTL.disj(goals) if disjunction else LTL.conj(goals)

        return [liveness_formula]


# =========================================================
# Entry point
# =========================================================

def main(): #pragma: no cover
	
	my_gr1_formula = GR1Formula()

if __name__ == "__main__": #pragma: no cover
	main()
