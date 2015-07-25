#!/usr/bin/env python

import unittest

from respec.spec.ic_specification import *
from respec.spec.robot_specification import *

class ICSpecificationTests(unittest.TestCase):
    """The calls to the method(s) handling new actions."""

    def setUp(self):
        """Gets called before every test case."""

        self.spec_name = 'test'

        self.spec = InitialConditionsSpecification(name = self.spec_name)

    def tearDown(self):
        """Gets called after every test case."""

        del self.spec_name, self.spec

    def test_input_to_object(self):

        self.assertEqual(self.spec_name, self.spec.spec_name)

    def test_ics_from_spec(self):
        
        other_spec = ActionSpecification()
        other_spec.handle_new_action(action = 'foo')
        other_spec.handle_new_action(action = 'bar')

        true_props = ['foo']
        expected_sys_init = ['foo_a', '! bar_a']
        expected_env_init = ['foo_c', '! bar_c']

        self.spec.set_ics_from_spec(other_spec, true_props)

        self.assertItemsEqual(actual_seq = self.spec.sys_init,
                              expected_seq = expected_sys_init)

        self.assertItemsEqual(actual_seq = self.spec.env_init,
                              expected_seq = expected_env_init)

# =============================================================================
# Entry point
# =============================================================================

if __name__ == '__main__':
    # Run all tests
    unittest.main()
