#!/usr/bin/env python

import os

from respec.spec.gr1_specification import GR1Specification
from respec.formula.gr1_formulas import GR1Formula, FastSlowFormula

import unittest

class FormulaGenerationTests(unittest.TestCase):

	# ==========================================
	# Tests for generic GR(1) formulas
	# ==========================================

	def setUp(self):
		"""Gets called before every test case."""

		self.env_props = ['x1', 'x2']
		self.sys_props = ['y1', 'y2', 'y3']

		print("Setting up a new formula test.")

	def tearDown(self):
		"""Gets called after every test case."""

		print("Cleaning up after latest test ...")

		del self.env_props
		del self.sys_props

	def test_props_from_ts(self):
		
		ts = {
			'a1': ['a1', 'a2'],
			'a2': ['a2', 'a3'],
			'a3': ['a3', 'a2']
		}

		expected_props = set(self.sys_props + ts.keys())

		formula = GR1Formula(self.env_props, self.sys_props, ts)

		self.assertSetEqual(set(formula.sys_props), expected_props)

	def test_mutex(self):
		"""Test whether mutual exclusion formulas are generated correctly."""

		formula = GR1Formula(self.env_props, self.sys_props)

		mutex = formula.gen_mutex_formulas(self.sys_props, False)

		expected_mutex = ["y1 <-> ! y2 & ! y3", "y2 <-> ! y1 & ! y3", "y3 <-> ! y1 & ! y2"]

		self.assertSetEqual(set(mutex), set(expected_mutex))

	def test_sys_trans(self):
		"""Test the adjacency relation that encodes the transition system."""

		ts = {
			'y1': ['y1', 'y2'],
			'y2': ['y2', 'y3'],
			'y3': ['y3', 'y2']
		}

		formula = GR1Formula(self.env_props, self.sys_props ,ts)

		adj_relation = formula.gen_sys_trans_formulas()
		# print adj_relation

		expected_adj_relation = [
			"y1 -> (y1 & ! y2 & ! y3)' | (y2 & ! y1 & ! y3)'",
			"y2 -> (y2 & ! y1 & ! y3)' | (y3 & ! y1 & ! y2)'",
			"y3 -> (y3 & ! y1 & ! y2)' | (y2 & ! y1 & ! y3)'"
		]

		self.assertSetEqual(set(adj_relation), set(expected_adj_relation))


if __name__ == '__main__':
	# Run all tests
	unittest.main()