#!/usr/bin/env python

import unittest

from respec.spec.gr1_specification import *

class SpecificationTests(unittest.TestCase):

	NAME = "test_refactoring" # without file extension

	#TODO: Move to test/spec/ as gr1_specification_test

	def setUp(self):
		"""Gets called before every test case."""
		
		self.name = SpecificationTests.NAME

		print("Setting up a new specification: %s" % self.name)

		self.env_props = ['x']
		self.sys_props = ['y1', 'y2']

		# self.sys_init = dict()
		# self.sys_init = {'y1': True, 'y2': False}
		# self.env_init = {'x': False}

		self.spec = GR1Specification(self.name, self.env_props, self.sys_props)

	def tearDown(self):
		"""Gets called after every test case."""

		#TODO: Make this more robust (e.g. if no dir exists)

		print("Cleaning up after latest test ...")

		test_dir = os.path.join(os.getcwd(), self.name)
		# files = [f for f in os.listdir(test_dir) if os.path.isfile(os.path.join(test_dir, f))]

		extensions = ['.structuredslugs', '.slugsin', '.aut', '.dot']
		
		# for f in files:
		# 	if any(f.lower().endswith(ext) for ext in extensions):
		# 		os.remove(os.path.join(test_dir, f))
		# 		print("Deleting file: %s" % str(f))

		del self.name
		del self.env_props
		del self.sys_props
		del self.spec

	def test_for_spec_file(self):
		"""Test whether specification object was created."""
		
		self.fail('Incomplete test!')
		self.failUnless(self.spec)

	def test_for_duplicate_env_props(self):
		self.fail('Incomplete test!')
		duplicate_env_props = len(self.spec.env_props) != len(set(self.spec.env_props))
		self.failIf(duplicate_env_props is True, "Some environment propositions appear more than once.")

	def test_for_duplicate_sys_props(self):
		self.fail('Incomplete test!')
		duplicate_sys_props = len(self.spec.sys_props) != len(set(self.spec.sys_props))
		self.failIf(duplicate_sys_props is True, "Some system propositions appear more than once.")

	def test_spec_file_generation(self):
		
		self.fail('Incomplete test!')

		self.spec.write_structured_slugs_file()

		full_file_path = os.path.join(self.name, self.name + ".structuredslugs")

		self.failUnless(os.path.isfile(full_file_path))