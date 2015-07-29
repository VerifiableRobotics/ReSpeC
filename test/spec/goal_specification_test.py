#!/usr/bin/env python

import unittest

from respec.spec.goal_specification import *

class SpecificationConstructionTests(unittest.TestCase):
    """Test the generation of Activation-Outcomes formulas"""

    def setUp(self):
        """Gets called before every test case."""

        self.spec_name = 'test'

        self.spec = GoalSpecification(name = self.spec_name)

    def tearDown(self):
        """Gets called after every test case."""

        del self.spec_name, self.spec

    def test_input_to_object(self):

        self.assertEqual(self.spec_name, self.spec.spec_name)

    def test_handle_single_goal(self):
        
        goal = 'dance'
        self.spec.handle_single_liveness(goals = [goal])

        expected_formula_0 = 'next(dance_c) -> next(dance_m)'
        expected_formula_1 = 'dance_m -> next(dance_m)'
        expected_formula_2 = '(! dance_m & next(! dance_c)) -> next(! dance_m)'
        expected_formula_3 = 'finished <-> dance_m'

        self.assertItemsEqual(actual_seq = self.spec.sys_trans,
                              expected_seq = [expected_formula_0, expected_formula_1,
                                              expected_formula_2, expected_formula_3])
        self.assertItemsEqual(actual_seq = self.spec.sys_liveness,
                              expected_seq = ['finished'])

    def test_handle_single_goal_failure_outcome(self):
        
        goal = 'dance'
        self.spec.handle_single_liveness(goals = [goal],
                                         outcomes = ['finished', 'failed'])
        self.spec.handle_any_failure(conditions = [goal],
                                     failure = 'failed')


        expected_formula_0 = 'next(dance_c) -> next(dance_m)'
        expected_formula_1 = 'dance_m -> next(dance_m)'
        expected_formula_2 = '(! dance_m & next(! dance_c)) -> next(! dance_m)'
        
        expected_formula_3 = 'finished <-> dance_m'
        expected_formula_4 = 'next(failed) <-> (next(dance_f) | failed)'

        self.assertItemsEqual(actual_seq = self.spec.sys_trans,
                              expected_seq = [expected_formula_0, expected_formula_1,
                                              expected_formula_2, expected_formula_3,
                                              expected_formula_4])

        self.assertItemsEqual(actual_seq = self.spec.sys_liveness,
                              expected_seq = ['(finished | failed)'])

    def test_handle_strict_goal_order(self):
        
        goals = ['dance', 'sleep', 'swim']
        self.spec.handle_single_liveness(goals = goals,
                                         outcomes = ['finished'],
                                         strict_order = True)

        expected_formula_1 = '! dance_m -> next(! sleep_m)'
        expected_formula_2 = '! sleep_m -> next(! swim_m)'

        self.assertIn(expected_formula_1, self.spec.sys_trans)
        self.assertIn(expected_formula_2, self.spec.sys_trans)

    def test_unsupported_outcomes_raise_exception(self):
        
        goal = 'dance'

        self.assertRaises(NotImplementedError, self.spec.handle_single_liveness,
                                               goals = [goal], outcomes = []) #0

        too_many_outcomes = ['finished', 'failed', 'thats_too_much'] # >2

        self.assertRaises(NotImplementedError, self.spec.handle_single_liveness,
                                               goals = [goal],
                                               outcomes = too_many_outcomes)
