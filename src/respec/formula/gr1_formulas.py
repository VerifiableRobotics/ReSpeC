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
					neg_prop = LTL.neg(LTL.next(prop_prime)) # not(next(p'))
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


class FastSlowFormula(GR1Formula):

	"""

	Arguments:
	  env_props (list of str)	Environment propositions (strings)
	  sys_props (list of str)	System propositions (strings)
	  ts 		(dict of str)	Transition system, TS (e.g. workspace topology)
	  							Implicitly contains some propositions in the keys.

	Attributes:
	  activation (list of str)	...
	  completion (list of str)	...
	  ts 		 (dict of str)	...

	Raises:
	  ValueError:				When a proposition is neither an activation or a completion proposition

	"""

	def __init__(self, env_props = [], sys_props = [], ts = {}):
		super(FastSlowFormula, self).__init__(env_props, sys_props, ts)

		self.activation = []
		self.completion = []

		self._gen_a_c_propositions()

		# Store the original (non fast-slow) TS,
		# then convert to a "fast-slow" transition system
		self.ts_original = ts
		self._convert_ts_to_fs()

	def _convert_ts_to_fs(self):
		"""..."""
		new_ts = {}

		for k in self.ts.keys():		
			k_c = self._get_c_prop(k) 		# completion prop

			k_c_values = list()
			for v in self.ts[k]:			
				v_a = self._get_a_prop(v) 	# activation prop

				k_c_values.append(v_a)

			new_ts[k_c] = k_c_values

		self.ts = new_ts

	def gen_init_fs_from_props(self, props):
		'''
		Given a list of propositions that are initially True, this method:	
		  * converts them to actication/completion props (if necessary) 
		  * prepares the corresponding prop assignment (dictionary)
		  * calls the two methods for getting the sys and env initial condition formulas
		  * returns both of them	
		'''

		prop_assignment_sys = dict()
		prop_assignment_env = dict()

		for p in props:
			
			if p in self.sys_props:
				p_init = self._get_a_prop(p)
				prop_assignment_sys[p_init] = True
			elif p in self.activation:
				p_init = p
				prop_assignment_sys[p_init] = True		
			elif p in self.env_props:
				p_init = self._get_c_prop(p)
				prop_assignment_env[p_init] = True
			elif p in self.completion:
				p_init = p
				prop_assignment_env[p_init] = True
			else:
				raise ValueError("Unknown type for proposition (fast-slow): %s" % p)

		sys_init = self.gen_sys_init_from_prop_assignment(prop_assignment_sys, 'activation')
		env_init = self.gen_env_init_from_prop_assignment(prop_assignment_env, 'completion')

		return sys_init, env_init

	# =====================================================
	# Activation / Competion (fast-slow) formulas
	# Equation and section numbers are w.r.t.
	# Vasumathi Raman and Hadas Kress-Gazit (ICRA 2013)
	# =====================================================

	def gen_fs_sys_transitions(self):
		"""
		Section V-B-2
		
		Encodes a transition system in terms of 'fast-slow' safety requirement formulas.
		"""

		# Present tense for fast-slow transition system formulas
		return self.gen_sys_trans_formulas(future = False)

	def gen_action_completion_formula(self, actions = []):
		"""
		Eq. (3-4)

		actions:	Propositions (NOT of the activation-completion type)
		"""
		
		actions = self.sys_props if not actions else actions

		eq3_formulas = list()
		eq4_formulas = list()

		for pi in actions:

			pi_c = self._get_c_prop(pi)
			pi_a = self._get_a_prop(pi)

			# Generate Eq. (3)
			eq3_left_hand_side = LTL.conj([pi_c, pi_a])
			eq3_right_hand_side = LTL.next(pi_c)
			eq3 = LTL.implication(eq3_left_hand_side, eq3_right_hand_side)
			eq3_formulas.append(eq3)

			# Generate Eq. (4)
			not_pi_c = LTL.neg(pi_c)
			not_pi_a = LTL.neg(pi_a)
			eq4_left_hand_side = LTL.conj([not_pi_c, not_pi_a])
			eq4_right_hand_side = LTL.next(not_pi_c)
			eq4 = LTL.implication(eq4_left_hand_side, eq4_right_hand_side)
			eq4_formulas.append(eq4)

		return eq3_formulas + eq4_formulas

	def gen_generic_fairness_formula(self, actions = []):
		"""
		From Section V-B (4)

		Fairness conditions ensure that every action eventually completes.
		"""
		
		actions = self.sys_props if not actions else actions

		fairness_formulas = list()

		for pi in actions:

			pi_c = self._get_c_prop(pi)
			pi_a = self._get_a_prop(pi)
			not_pi_c = LTL.neg(pi_c)
			not_pi_a = LTL.neg(pi_a)

			completion_disjunct_1 = LTL.conj([pi_a, LTL.next(pi_c)])
			completion_disjunct_2 = LTL.conj([not_pi_a, LTL.next(not_pi_c)])
			completion_formula = LTL.disj([completion_disjunct_1, completion_disjunct_2])

			change_disjunt_1 = LTL.conj([pi_a, LTL.next(not_pi_a)])
			change_disjunt_2 = LTL.conj([not_pi_a, LTL.next(pi_a)])
			change_formula = LTL.disj([change_disjunt_1, change_disjunt_2])

			fairness_condition = LTL.disj([completion_formula, change_formula])

			fairness_formulas.append(fairness_condition)

		return fairness_formulas

	def gen_mutex_fairness_formula(self):
		"""
		From Section V-B (4)

		Generates environment fairness conditions for the special case of 
		mutually exclusive propositions, such as regions of the workspace.
		Specifically, these propositions are encoded as a transition system.
		"""
		
		completion_terms = list()
		change_terms = list()

		for pi in self.ts_original.keys():

			pi_a = self._get_a_prop(pi)
			phi = self._gen_phi_prop(pi_a)

			pi_c = self._get_c_prop(pi)
			next_pi_c = LTL.next(pi_c)
			not_next_phi = LTL.neg(LTL.next(phi))

			completion_term = LTL.paren(LTL.conj([phi, next_pi_c]))
			completion_terms.append(completion_term)
			
			change_term = LTL.paren(LTL.conj([phi, not_next_phi]))
			change_terms.append(change_term)

		completion_formula = LTL.disj(completion_terms)
		change_formula = LTL.disj(change_terms)
		fairness_formula = LTL.disj([completion_formula, change_formula])

		return fairness_formula

	def gen_single_step_change_formula(self):
		"""Eq. (2)"""

		all_formulas = list()

		for pi in self.ts_original.keys():
			
			for pi_prime in self.ts_original[pi]:
				pi_c = self._get_c_prop(pi)
				pi_prime_a = self._get_a_prop(pi_prime)
				phi = self._gen_phi_prop(pi_prime_a)

				left_hand_side = LTL.conj([pi_c, phi])

				next_pi_c = LTL.next(pi_c)
				pi_prime_c = self._get_c_prop(pi_prime)
				next_pi_prime_c = LTL.next(pi_prime_c)

				if next_pi_c == next_pi_prime_c:
					right_hand_side = next_pi_prime_c
				else:
					right_hand_side = LTL.paren(LTL.disj([next_pi_c, next_pi_prime_c]))

				implication = LTL.implication(left_hand_side, right_hand_side)

				all_formulas.append(implication)

		return all_formulas

	# =====================================================
	# Various helper methods specific to fast-slow formulas
	# =====================================================

	def gen_memory_prop(self, prop):
		'''
		Creates a memory proposition from the given proposition
		and adds the memory proposition to the system propositions.'''

		if self._is_completion(prop):
			mem_prop = prop.replace('_c', '_m')
		else:
			mem_prop = prop + '_m'

		self.sys_props.append(mem_prop)

		return mem_prop

	def _gen_a_c_propositions(self):
		"""
		For each system proposition (action, region ,etc.), create the corresponding activation and completion propositions.		
		"""

		for sys_prop in self.sys_props:		
			if not self._is_activation(sys_prop):			
				# Add activation proposition and mark original system proposition for removal
				self.activation.append(self._get_a_prop(sys_prop))
				# Also add the corresponding completion proposition
				self.completion.append(self._get_c_prop(sys_prop))

	def _get_other_trans_props(self, prop):
		"""For some proposition \pi_r, get all propositions \pi_r' such that r' =/= r."""
		
		if prop in self.activation:
			return [p for p in self.activation if p != prop]
		elif prop in self.completion:
			return [p for p in self.completion if p != prop]
		else:
			raise ValueError("Unknown type for proposition (fast-slow): %s" % prop)

	def _get_a_prop(self, prop):
		return prop + "_a"

	def _get_c_prop(self, prop):
		return prop + "_c"

	def _is_activation(self, prop):
		return prop[-2:] == "_a"

	def _is_completion(self, prop):
		return prop[-2:] == "_c"


# =========================================================
# Entry point
# =========================================================

def main(): #pragma: no cover
	
	my_gr1_formula = GR1Formula()
	my_fs_formula = FastSlowFormula()

if __name__ == "__main__": #pragma: no cover
	main()
