#!/usr/bin/env python

import os

import unittest

from respec.spec import GR1Specification

class SpecificationTests(unittest.TestCase):

	def setUp(self):
		
		self.name = "test_refactoring" # without file extension
		self.test_dir = os.path.dirname(__file__)

		self.env_props = ['x']
		self.sys_props = ['y1', 'y2']

		# self.sys_init = dict()
		# self.sys_init = {'y1': True, 'y2': False}
		# self.env_init = {'x': False}

		self.spec = GR1Specification(self.name, self.env_props, self.sys_props)

	def tearDown(self):

		print("Cleaning up after latest test ...")

		test_spec_dir = os.path.join(self.test_dir, self.name)
		
		if os.path.isdir(test_spec_dir):
			
			files = [f for f in os.listdir(test_spec_dir)
					if os.path.isfile(os.path.join(test_spec_dir, f))]

			extensions = ['.structuredslugs', '.slugsin', '.aut', '.dot']
		
			for f in files:
				if any(f.lower().endswith(ext) for ext in extensions):
					os.remove(os.path.join(test_spec_dir, f))
					print("Deleting file: %s" % str(f))

			os.rmdir(test_spec_dir)
			print("Deleting directory: %s" % str(test_spec_dir))

		del self.name
		del self.test_dir
		del self.env_props
		del self.sys_props
		del self.spec

	def test_spec_constructor(self):
		
		self.failUnless(self.spec)
		self.assertEqual(self.name, self.spec.spec_name)
		self.assertItemsEqual(self.env_props, self.spec.env_props)
		self.assertItemsEqual(self.sys_props, self.spec.sys_props)

	def test_spec_file_generation(self):
		
		self.spec.write_structured_slugs_file(folder_path = self.test_dir)

		full_file_path = os.path.join(self.test_dir, self.name,
									  self.name + ".structuredslugs")

		self.failUnless(os.path.isfile(full_file_path))
