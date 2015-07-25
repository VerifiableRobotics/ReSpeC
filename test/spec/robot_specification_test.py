#!/usr/bin/env python

import unittest

from respec.spec.robot_specification import *


class ActionSpecificationTests(unittest.TestCase):
    """The calls to the method(s) handling new actions."""

    def setUp(self):
        """Gets called before every test case."""

        self.spec_name = 'test'
        self.preconditions = {'run': ['step', 'walk'],
                              'bar': ['foo'],
                              'fu' : ['bar'],
                              'foo': None}

        self.spec = ActionSpecification(name = self.spec_name,
                                        preconditions = self.preconditions)

    def tearDown(self):
        """Gets called after every test case."""

        del self.spec_name, self.spec

    def test_input_to_object(self):

        self.assertEqual(self.spec_name, self.spec.spec_name)
        self.assertEqual(self.preconditions, self.spec.preconditions)

    def test_formulas_from_preconditions(self):
        
        action = 'bar'
        formula = self.spec._gen_preconditions_formula(action, act_out = True,
                                                       outcomes = ['completed'])

        self.spec.handle_new_action(action)

        expected_formula = '! foo_c -> ! bar_a'

        self.assertIsInstance(formula, PreconditionsFormula)
        self.assertEqual(expected_formula, formula.formulas[0])

    def test_not_act_out_raises_exception(self):

        action = self.preconditions.keys()[0]
        self.assertRaises(NotImplementedError,
                          self.spec._gen_preconditions_formula,
                          action, False, ['completed'])

    def test_action_not_in_preconditions_config(self):
        
        action = 'i_am_not_in_the_dict'
        self.spec.handle_new_action(action)
        #FIX: This assertion will fail once more formulas are added
        self.assertEqual(len(self.spec.sys_trans), 1) # 1 for deactivation

    def test_action_without_preconditions(self):
        
        action = 'foo'
        self.spec.handle_new_action(action)
        #FIX: This assertion will fail once more formulas are added
        self.assertEqual(len(self.spec.sys_trans), 1) # 1 for deactivation

    def test_recursive_preconditions(self):

        action = 'fu'
        self.spec.handle_new_action(action)

        expected_formula_0 = '! foo_c -> ! bar_a'
        expected_formula_1 = '! bar_c -> ! fu_a'

        self.assertIn(expected_formula_0, self.spec.sys_trans)
        self.assertIn(expected_formula_1, self.spec.sys_trans)
        #FIX: This assertion will fail once more formulas are added
        self.assertEqual(len(self.spec.sys_trans), 5) # 2 preconditions + 3 deactivation
        
    def test_handle_new_action_with_multiple_preconditions(self):
        
        action = 'run'
        self.spec.handle_new_action(action)

        expected_formula_0 = '(run_c & run_a) -> next(run_c)' # outcome
        expected_formula_1 = '(! run_c & ! run_a) -> next(! run_c)' # outcome
        expected_formula_2 = '(run_c & ! run_a) -> next(run_c)' # peristence
        expected_formula_3 = '(run_a & next(run_c)) -> next(! run_a)' # deactivation
        expected_formula_4 = '(! step_c | ! walk_c) -> ! run_a' # preconditions
        
        expected_formula_5a = '((run_a & next(run_c)) | (! run_a & next(! run_c)) | (! run_a & next(run_c)))'
        expected_formula_5b = '((run_a & next(! run_a)) | (! run_a & next(run_a)))'
        expected_formula_5  = '(' + expected_formula_5a + ' | ' + \
                                    expected_formula_5b + ')' # fairness condition

        self.assertItemsEqual(actual_seq = self.spec.env_trans,
                              expected_seq = [expected_formula_0,
                                              expected_formula_1,
                                              expected_formula_2])
        self.assertItemsEqual(actual_seq = self.spec.sys_trans,
                              expected_seq = [expected_formula_3, expected_formula_4])
        self.assertItemsEqual(actual_seq = self.spec.env_liveness,
                              expected_seq = [expected_formula_5])

    def test_handle_multiple_outcomes(self):
        
        action = 'run'
        self.spec.handle_new_action(action, outcomes = ['completed', 'failed'])

        expected_formula_0 = '((run_c | run_f) & run_a) -> (next(run_c) | next(run_f))' # outcome
        expected_formula_1a = '(! run_c & ! run_a) -> next(! run_c)' # outcome
        expected_formula_1b = '(! run_f & ! run_a) -> next(! run_f)' # outcome
        expected_formula_1c = '(run_c & ! run_a) -> next(run_c)' # persistence
        expected_formula_1d = '(run_f & ! run_a) -> next(run_f)' # persistence
        expected_formula_2 = '(run_a & (next(run_c) | next(run_f))) -> next(! run_a)' # deactivation
        expected_formula_3 = '(! step_c | ! walk_c) -> ! run_a' # preconditions
        expected_formula_4a = '(run_a & (next(run_c) | next(run_f)))'
        expected_formula_4b = '(! run_a & (next(! run_c) & next(! run_f)))'
        expected_formula_4c = '(! run_a & (next(run_c) | next(run_f)))'
        expected_formula_4  = '(' + expected_formula_4a + ' | ' + \
                                 expected_formula_4b + ' | ' + \
                                 expected_formula_4c + ')'
        expected_formula_4d = '((run_a & next(! run_a)) | (! run_a & next(run_a)))'
        expected_formula_4 = '(' + expected_formula_4 + ' | ' + \
                              expected_formula_4d + ')' # fairness condition
        expected_formula_5a = 'next(run_c) -> next(! run_f)' # mutex
        expected_formula_5b = 'next(run_f) -> next(! run_c)' # mutex

        self.assertItemsEqual(actual_seq = self.spec.env_trans,
                              expected_seq = [expected_formula_0,
                                expected_formula_1a, expected_formula_1b,
                                expected_formula_1c, expected_formula_1d,
                                expected_formula_5a, expected_formula_5b])
        self.assertItemsEqual(actual_seq = self.spec.sys_trans,
                              expected_seq = [expected_formula_2,
                                              expected_formula_3])
        self.assertItemsEqual(actual_seq = self.spec.env_liveness,
                              expected_seq = [expected_formula_4])


    def test_handle_recursive_preconditions_with_multiple_outcomes(self):
        self.fail('Incomplete test!')

class ConfigurationTests(unittest.TestCase):
    """Test the construction of the RobotConfiguration class."""

    def setUp(self):
        """Gets called before every test case."""

        self.robot = 'atlas'

        self.config = RobotConfiguration(robot = self.robot)

    def tearDown(self):
        """Gets called after every test case."""

        del self.config

    def test_input_to_object(self):

        self.assertEqual(self.robot, self.config._robot)

    def test_load_config_file(self):
    	
    	self.assertIsInstance(self.config._full_config, dict)
    	self.assertIsInstance(self.config.ts, dict)
    	self.assertIsInstance(self.config.preconditions, dict)

    def test_incorrect_input(self):
    	
    	self.config = RobotConfiguration(robot = 'bad_robot_name')

    	self.assertItemsEqual(self.config._full_config, dict())
    	self.assertItemsEqual(self.config.ts, dict())
    	self.assertItemsEqual(self.config.preconditions, dict())

# =============================================================================
# Entry point
# =============================================================================

if __name__ == '__main__':
    # Run all tests
    unittest.main()
