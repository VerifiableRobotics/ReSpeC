#!/usr/bin/env python

"""
Specification written in the GR(1) fragment of Linear Temporal Logic

This module contains one class, GR1Specification.
A GR(1) Specification consists of propositions and formulas.

The class has (private) methods for populating the 6 parts of a GR(1) formula:
  * Environment initial conditions
  * Environment safety assumptions
  * Environment fairness (liveness) assumptions (aka, environment goals)
  * System initial conditions
  * System safety requirements
  * System liveness requirements (aka, system goals)
From the outside, formulas can be added using the method(s) for loading.

Multiple GR1Specification objects can be merged.
Merging is both proposition-wise and formula-wise.

There are also (public) methods for writing the specification in 
a .structuredslugs file for use with the SLUGS synthesis tool:

https://github.com/LTLMoP/slugs

"""

import os

class GR1Specification(object):
	"""
	The class encodes the GR(1) fragment of LTL formulas. 
	The formulas are written in the structured slugs format.
	(See https://github.com/LTLMoP/slugs/blob/master/doc/input_formats.md)

	Arguments:
	  spec_name	(str)			The name of the specification.
	  							The spec file will be named like that.
	  env_props	(list of str)	Environment (input) propositions
	  sys_props	(list of str)	System (output) propositions
	
	"""

	def __init__(self, spec_name = '', env_props = [], sys_props = []):
		self.spec_name = spec_name

		self.env_props = env_props	
		self.sys_props = sys_props

		# Initialize the six GR(1) subformulas
		self.sys_init  = list()
		self.env_init  = list()
		self.sys_trans = list()
		self.env_trans = list()
		self.sys_liveness = list()
		self.env_liveness = list()

	# =====================================================
	# Merge two or more GR(1) specifications
	# =====================================================

	def merge_gr1_specifications(self, specifications):
		'''Component-wise merger of multiple GR(1) specifications.'''
		
		for spec in specifications:

			self.env_props = self.merge_env_propositions(spec.env_props)
			self.sys_props = self.merge_sys_propositions(spec.sys_props)

			self.sys_init.extend(spec.sys_init)
			self.env_init.extend(spec.env_init)
			self.sys_trans.extend(spec.sys_trans)
			self.env_trans.extend(spec.env_trans)
			self.sys_liveness.extend(spec.sys_liveness)
			self.env_liveness.extend(spec.env_liveness)

	def merge_env_propositions(self, props):
		return self.merge_propositions('env_props', props)

	def merge_sys_propositions(self, props):
		return self.merge_propositions('sys_props', props)

	def merge_propositions(self, desired_list, props):
		'''Merge list of propositions without duplication.'''

		all_props = getattr(self, desired_list)
		all_props.extend(props)

		# Return list of props without duplicates
		return list(set(all_props))

	# =====================================================
	# Load a GR(1) formula
	# =====================================================

	def load_formulas(self, formulas):
		"""Load multiple GR1Formulas into the GR(1) specification."""
		
		for formula in formulas:
			self.load(formula)

	def load(self, formula):
		"""Load an object of type GR1Formula into the GR(1) specification."""
		
		self.env_props = self.merge_env_propositions(formula.env_props)
		self.sys_props = self.merge_sys_propositions(formula.sys_props)

		try:
			self._add_to_list(formula.type, formula.formulas)
		except Exception as e:
			print e
			raise ValueError('The {formula} has type {type}. Loading failed!'
							 .format(formula = formula.__class__.__name__,
							 		 type = formula.type))


	# =====================================================
	# "Setter"-type methods for the 6 types of subformulas
	# =====================================================

	# The public setter methods have been replaced by load and load_formulas

	# def add_to_sys_init(self, formulas):	
	# 	self._add_to_list('sys_init', formulas)

	# def add_to_env_init(self, formulas):
	# 	self._add_to_list('env_init', formulas)

	# def add_to_sys_trans(self, formulas):	
	# 	self._add_to_list('sys_trans', formulas)

	# def add_to_env_trans(self, formulas):
	# 	self._add_to_list('env_trans', formulas)

	# def add_to_sys_liveness(self, formulas):
	# 	self._add_to_list('sys_liveness', formulas)

	# def add_to_env_liveness(self, formulas):
	# 	self._add_to_list('env_liveness', formulas)

	def _add_to_list(self, desired_list, thing_to_add):
		"""
		Generic method for appending to, or extending,
		a list attribute of the object (e.g. self.sys_liveness)
		"""

		if type(thing_to_add) is str:
			getattr(self, desired_list).append(thing_to_add)
		elif type(thing_to_add) is list:
			getattr(self, desired_list).extend(thing_to_add)
		elif thing_to_add is None:
			print("Warning: Nothing was added to {}!".format(desired_list))
		else:
			raise ValueError("Invalid input: {} \
							  Add either a string or a list of strings."
							 .format(str(thing_to_add)))

	# =====================================================
	# Composition of the Structured SLUGS file
	# =====================================================

	def write_structured_slugs_file(self, folder_path):
		"""Open a structuredslugs file and write the 8 sections."""	
		
		filename = self.spec_name + ".structuredslugs"

		folder_path = os.path.join(folder_path, self.spec_name)

		if not os.path.exists(folder_path):
			os.makedirs(folder_path)

		# Get /home/path_to_file/file.structuredslugs
		full_file_path = os.path.join(folder_path, filename)
		
		with open(full_file_path, 'w') as spec_file:
			# System and environment propositions
			self._write_input(spec_file)
			self._write_output(spec_file)
			# Initial Conditions
			self._write_sys_init(spec_file)
			self._write_env_init(spec_file)
			# Safety Requirements & Assumptions
			self._write_sys_trans(spec_file)
			self._write_env_trans(spec_file)
			# Liveness Requirements & Assumptions
			self._write_sys_liveness(spec_file)
			self._write_env_liveness(spec_file)

		print("\nCreated specification file {name} in {dir} \n"
			  .format(name = filename, dir = folder_path))

		return full_file_path, folder_path

	def _write_input(self, spec_file):
		spec_file.write("[INPUT]\n")
		for prop in self.env_props:
			spec_file.write(prop + "\n")
		spec_file.write("\n")

	def _write_output(self, spec_file):
		spec_file.write("[OUTPUT]\n")
		for prop in self.sys_props:
		    spec_file.write(prop + "\n")
		spec_file.write("\n")

	def _write_sys_init(self, spec_file):
		spec_file.write("[SYS_INIT]\n")
		for formula in self.sys_init:
			spec_file.write(formula + "\n")
		spec_file.write("\n")

	def _write_env_init(self, spec_file):
		spec_file.write("[ENV_INIT]\n")
		for formula in self.env_init:
			spec_file.write(formula + "\n")
		spec_file.write("\n")

	def _write_sys_trans(self, spec_file):
		spec_file.write("[SYS_TRANS]\n")
		for formula in self.sys_trans:
			spec_file.write(formula + "\n")
		spec_file.write("\n")

	def _write_env_trans(self, spec_file):
		spec_file.write("[ENV_TRANS]\n")
		for formula in self.env_trans:
			spec_file.write(formula + "\n")
		spec_file.write("\n")

	def _write_sys_liveness(self, spec_file):
		spec_file.write("[SYS_LIVENESS]\n")
		for formula in self.sys_liveness:
			spec_file.write(formula + "\n")
		spec_file.write("\n")

	def _write_env_liveness(self, spec_file):
		spec_file.write("[ENV_LIVENESS]\n")
		for formula in self.env_liveness:
			spec_file.write(formula + "\n")
		spec_file.write("\n")


# =========================================================
# Entry point
# =========================================================

def main(): #pragma: no cover
	
	pass

if __name__ == "__main__": #pragma: no cover
	main()
	