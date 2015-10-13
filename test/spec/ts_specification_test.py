#!/usr/bin/env python

import unittest

from respec.spec.ts_specification import *

class SpecificationConstructionTests(unittest.TestCase):
    """Test the generation of Activation-Outcomes formulas"""

    def setUp(self):
        """Gets called before every test case."""

        self.spec_name = 'test'
        self.ts = {'r1': ['r1', 'r2', 'r3'],
                   'r2': ['r2'],
                   'r3': ['r3', 'r1']}

        self.spec = TransitionSystemSpecification(name = self.spec_name,
                                                  ts = self.ts,
                                                  outcomes = ['completed', 'failed'])

    def tearDown(self):
        """Gets called after every test case."""

        del self.ts, self.spec

    def test_input_to_object(self):

        self.assertEqual(self.spec_name, self.spec.spec_name)
        self.assertItemsEqual(self.ts, self.spec.ts)

    def test_ts_of_interest(self):
 
        props = ['r1', 'r3']
        ts_of_interest = {'r1': ['r1', 'r3'],
                          'r3': ['r3', 'r1']}

        self.spec = TransitionSystemSpecification(ts = self.ts,
                                                  props_of_interest = props)
        
        self.assertItemsEqual(ts_of_interest, self.spec.ts)

    def test_formulas_in_env_trans(self):

        expected_formula_1a = 'next(r1_c) <-> (! next(r2_c) & ! next(r3_c))'
        expected_formula_1b = 'next(r2_c) <-> (! next(r1_c) & ! next(r3_c))'
        expected_formula_1c = 'next(r3_c) <-> (! next(r1_c) & ! next(r2_c))'
        expected_formulas_1 = [expected_formula_1a, expected_formula_1b, expected_formula_1c] # mutex

        expected_formula_2a = '(r1_c & (r1_a & ! r2_a & ! r3_a)) -> (next(r1_c) | next(r1_f))'
        expected_formula_2b = '(r1_c & (r2_a & ! r1_a & ! r3_a)) -> (next(r1_c) | next(r2_f) | next(r2_c))'
        expected_formula_2c = '(r1_c & (r3_a & ! r1_a & ! r2_a)) -> (next(r3_c) | next(r3_f) | next(r1_c))'
        expected_formula_2d = '(r2_c & (r2_a & ! r1_a & ! r3_a)) -> (next(r2_f) | next(r2_c))'
        expected_formula_2e = '(r3_c & (r1_a & ! r2_a & ! r3_a)) -> (next(r3_c) | next(r1_c) | next(r1_f))'
        expected_formula_2f = '(r3_c & (r3_a & ! r1_a & ! r2_a)) -> (next(r3_c) | next(r3_f))'
        expected_formulas_2 = [expected_formula_2a, expected_formula_2b,
                               expected_formula_2c, expected_formula_2d,
                               expected_formula_2e, expected_formula_2f] # single step

        expected_formula_3d = '(! r1_c & ! r1_a) -> next(! r1_c)'
        expected_formula_3e = '(! r2_c & ! r2_a) -> next(! r2_c)'
        expected_formula_3f = '(! r3_c & ! r3_a) -> next(! r3_c)'
        expected_formula_3g = '(! r1_f & ! r1_a) -> next(! r1_f)'
        expected_formula_3h = '(! r2_f & ! r2_a) -> next(! r2_f)'
        expected_formula_3i = '(! r3_f & ! r3_a) -> next(! r3_f)'

        expected_formulas_3 = [expected_formula_3d, expected_formula_3e, expected_formula_3f, # constrain completion
                               expected_formula_3g, expected_formula_3h, expected_formula_3i] # constrain failure

        expected_formula_4a = 'next(r1_c) -> next(! r1_f)'
        expected_formula_4b = 'next(r1_f) -> next(! r1_c)'
        expected_formula_4c = 'next(r2_c) -> next(! r2_f)'
        expected_formula_4d = 'next(r2_f) -> next(! r2_c)'
        expected_formula_4e = 'next(r3_c) -> next(! r3_f)'
        expected_formula_4f = 'next(r3_f) -> next(! r3_c)'

        expected_formulas_4 = [expected_formula_4a, expected_formula_4b, expected_formula_4c, # outcome mutex
                               expected_formula_4d, expected_formula_4e, expected_formula_4f]

        expected_formula_5a = '(r1_c & (! r1_a & ! r2_a & ! r3_a)) -> next(r1_c)'
        expected_formula_5b = '(r1_f & (! r1_a & ! r2_a & ! r3_a)) -> next(r1_f)'
        expected_formula_5c = '(r2_c & (! r1_a & ! r2_a & ! r3_a)) -> next(r2_c)'
        expected_formula_5d = '(r2_f & (! r1_a & ! r2_a & ! r3_a)) -> next(r2_f)'
        expected_formula_5e = '(r3_c & (! r1_a & ! r2_a & ! r3_a)) -> next(r3_c)'
        expected_formula_5f = '(r3_f & (! r1_a & ! r2_a & ! r3_a)) -> next(r3_f)'

        expected_formulas_5 = [expected_formula_5a, expected_formula_5b, expected_formula_5c, # outcome persistence
                               expected_formula_5d, expected_formula_5e, expected_formula_5f]

        expected_env_trans = expected_formulas_1 + expected_formulas_2 + \
                             expected_formulas_3 + expected_formulas_4 + \
                             expected_formulas_5

        self.assertItemsEqual(actual_seq = self.spec.env_trans,
                              expected_seq = expected_env_trans)

    def test_formulas_in_sys_trans(self):

        expected_formula_1 = 'next(r1_c) -> (next(r1_a & ! r2_a & ! r3_a) | ' + \
                                            'next(r2_a & ! r1_a & ! r3_a) | ' + \
                                            'next(r3_a & ! r1_a & ! r2_a) | ' + \
                                            'next(! r1_a & ! r2_a & ! r3_a))'
        expected_formula_2 = 'next(r2_c) -> (next(r2_a & ! r1_a & ! r3_a) | ' + \
                                            'next(! r1_a & ! r2_a & ! r3_a))'
        expected_formula_3 = 'next(r3_c) -> (next(r3_a & ! r1_a & ! r2_a) | ' + \
                                            'next(r1_a & ! r2_a & ! r3_a) | ' + \
                                            'next(! r1_a & ! r2_a & ! r3_a))'

        expected_formula_4a = '(r1_a & (next(r1_c) | next(r1_f))) -> next(! r1_a)'
        expected_formula_4b = '(r2_a & (next(r2_c) | next(r2_f))) -> next(! r2_a)'
        expected_formula_4c = '(r3_a & (next(r3_c) | next(r3_f))) -> next(! r3_a)'

        expected_sys_trans = [expected_formula_1, expected_formula_2, expected_formula_3, # transition relation
                              expected_formula_4a, expected_formula_4b, expected_formula_4c] # deactivation

        self.assertItemsEqual(actual_seq = self.spec.sys_trans,
                              expected_seq = expected_sys_trans)

    def test_formulas_in_env_liveness(self):
        
        expected_formula_1a = '((r1_a & ! r2_a & ! r3_a) & (next(r1_c) | next(r1_f)))'
        expected_formula_1b = '((r2_a & ! r1_a & ! r3_a) & (next(r2_c) | next(r2_f)))'
        expected_formula_1c = '((r3_a & ! r1_a & ! r2_a) & (next(r3_c) | next(r3_f)))'
        expected_formula_1  = '(' + expected_formula_1a + ' | ' + \
                                    expected_formula_1b + ' | ' + \
                                    expected_formula_1c + ')' # completion
        
        # expected_formula_2a = '((r1_a & ! r2_a & ! r3_a) & ! next(r1_a & ! r2_a & ! r3_a))'
        # expected_formula_2b = '((r2_a & ! r1_a & ! r3_a) & ! next(r2_a & ! r1_a & ! r3_a))'
        # expected_formula_2c = '((r3_a & ! r1_a & ! r2_a) & ! next(r3_a & ! r1_a & ! r2_a))'
        # expected_formula_2  = '(' + expected_formula_2a + ' | ' + \
        #                             expected_formula_2b + ' | ' + \
        #                             expected_formula_2c + ')' # change
        
        expected_formula_3 = '(! r1_a & ! r2_a & ! r3_a)' # activate nothing

        # expected_env_liveness = '(' + expected_formula_1 + ' | ' + \
        #                          expected_formula_2 + ' | ' + \
        #                          expected_formula_3 + ')'
        expected_env_liveness = '(' + expected_formula_1 + ' | ' + \
                                 expected_formula_3 + ')'

        self.assertItemsEqual(actual_seq = self.spec.env_liveness,
                              expected_seq = [expected_env_liveness])

# =============================================================================
# Entry point
# =============================================================================

if __name__ == '__main__':
    # Run all tests
    unittest.main()