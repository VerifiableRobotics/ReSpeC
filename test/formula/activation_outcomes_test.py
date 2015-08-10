#!/usr/bin/env python

from respec.formula.activation_outcomes import *

import unittest


class ActionFormulaGenerationTests(unittest.TestCase):
    """Test the generation of Activation-Outcomes action formulas"""

    def setUp(self):
        """Gets called before every test case."""

        self.sys_props = ['dance', 'sleep']
        self.outcomes  = ['completed', 'failed', 'preempted']

    def tearDown(self):
        """Gets called after every test case."""

        del self.sys_props
        del self.outcomes

    def test_base_class(self):

        formula = ActivationOutcomesFormula(self.sys_props, self.outcomes)

        # Test whether the obvious things are working as expected
        self.assertItemsEqual(self.outcomes, formula.outcomes)
        self.assertEqual(list(), formula.formulas)

        # Test whether the activation propositions are generated correctly
        expected_act_props = ['sleep_a', 'dance_a']
        self.assertItemsEqual(expected_act_props, formula.sys_props)

        # Test whether the outcome propositions are generated correctly
        expected_out_props = {'dance': ['dance_c', 'dance_f', 'dance_p'],
                              'sleep': ['sleep_c', 'sleep_f', 'sleep_p']}
        self.assertItemsEqual(expected_out_props, formula.outcome_props)

        # Test whether the environment propositions are generated correctly
        expected_env_props = ['dance_c', 'dance_f', 'dance_p',
                              'sleep_c', 'sleep_f', 'sleep_p']
        self.assertItemsEqual(expected_env_props, formula.env_props)

    def test_constructor_raises_exceptions(self):

        self.assertRaises(TypeError,  ActivationOutcomesFormula, ['dance', 1.0])
        self.assertRaises(ValueError, ActivationOutcomesFormula, ['dance_a'])
        self.assertRaises(ValueError, ActivationOutcomesFormula, ['dance'],[])
        self.assertRaises(TypeError,  ActivationOutcomesFormula, ['dance'],[2])
        self.assertRaises(ValueError, ActivationOutcomesFormula, ['dance'],
                          ['completed', 'capitalized', 'called', 'calculated'])

    def test_bad_activation_prop_request_raises_exception(self):
        
        from respec.formula.activation_outcomes import _get_act_prop

        self.assertRaises(ValueError, _get_act_prop, 'dance_a')

    def test_outcome_prop_from_activation(self):
        
        from respec.formula.activation_outcomes import _get_out_prop

        self.assertEqual(_get_out_prop('dance_a', 'failed'), 'dance_f')

    def test_mutex_formula(self):

        formula = OutcomeMutexFormula(['dance'],
                                      ['completed', 'failed', 'preempted'])

        expected_formula_c = 'next(dance_c) -> (next(! dance_f) & next(! dance_p))'
        expected_formula_f = 'next(dance_f) -> (next(! dance_c) & next(! dance_p))'
        expected_formula_p = 'next(dance_p) -> (next(! dance_c) & next(! dance_f))'

        expected_formulas = [expected_formula_c, expected_formula_f, expected_formula_p]

        self.assertEqual('env_trans', formula.type)
        self.assertItemsEqual(expected_formulas, formula.formulas)

    def test_mutex_single_outcome(self):

        formula = OutcomeMutexFormula(['dance'], outcomes = ['completed'])

        self.assertItemsEqual(list(), formula.formulas)

    def test_action_deactivation_formula_single_outcome(self):
        
        formula = PropositionDeactivationFormula(['dance', 'sleep'])

        expected_formula_1 = '(dance_a & next(dance_c)) -> next(! dance_a)'
        expected_formula_2 = '(sleep_a & next(sleep_c)) -> next(! sleep_a)'

        expected_formulas = [expected_formula_1, expected_formula_2]

        self.assertItemsEqual(expected_formulas, formula.formulas)

    def test_action_deactivation_formula_multiple_outcomes(self):
        
        formula = PropositionDeactivationFormula(
                                    sys_props = ['dance', 'sleep'],
                                    outcomes = ['completed', 'failed'])

        self.assertEqual('sys_trans', formula.type)

        expected_formula_1 = '(dance_a & (next(dance_c) | next(dance_f))) -> next(! dance_a)'
        expected_formula_2 = '(sleep_a & (next(sleep_c) | next(sleep_f))) -> next(! sleep_a)'

        expected_formulas = [expected_formula_1, expected_formula_2]

        self.assertItemsEqual(expected_formulas, formula.formulas)

    def test_action_outcome_constraints(self):
        
        formula = ActionOutcomeConstraintsFormula(
                                    actions = ['dance'],
                                    outcomes = ['completed', 'failed'])

        self.assertEqual('env_trans', formula.type)

        expected_formula_1 = '((dance_c | dance_f) & dance_a) -> (next(dance_c) | next(dance_f))'
        expected_formula_2a = '(! dance_c & ! dance_a) -> next(! dance_c)'
        expected_formula_2b = '(! dance_f & ! dance_a) -> next(! dance_f)'

        expected_formulas = [expected_formula_1,
                             expected_formula_2a, expected_formula_2b]

        self.assertItemsEqual(expected_formulas, formula.formulas)

    def test_action_outcome_persistence(self):
        
        formula = ActionOutcomePersistenceFormula(
                                    actions = ['dance'],
                                    outcomes = ['completed', 'failed'])

        self.assertEqual('env_trans', formula.type)

        expected_formula_1 = '(dance_c & ! dance_a) -> next(dance_c)'
        expected_formula_2 = '(dance_f & ! dance_a) -> next(dance_f)'

        expected_formulas = [expected_formula_1, expected_formula_2]

        self.assertItemsEqual(expected_formulas, formula.formulas)

    def test_action_fairness_conditions_multiple_outcomes(self):
        
        formula = ActionFairnessConditionsFormula(
                                    actions = ['dance'],
                                    outcomes = ['completed', 'failed'])

        expected_formula_1a = '(dance_a & (next(dance_c) | next(dance_f)))' # outcome
        expected_formula_1b = '(! dance_a & (next(! dance_c) & next(! dance_f)))' # deactivation ??
        expected_formula_1c = '(! dance_a & (next(dance_c) | next(dance_f)))' # persistence
        expected_formula_1  = '(' + expected_formula_1a + ' | ' + \
                                 expected_formula_1b + ' | ' + \
                                 expected_formula_1c + ')'
        expected_formula_2a = '(dance_a & next(! dance_a))'
        expected_formula_2b = '(! dance_a & next(dance_a))' # change
        expected_formula_2  = '(' + expected_formula_2a + ' | ' + \
                                 expected_formula_2b + ')'
        
        expected_formula = '(' + expected_formula_1 + ' | ' + \
                                 expected_formula_2 + ')'

        self.assertItemsEqual([expected_formula], formula.formulas)

    def test_preconditions_formula(self):
        
        formula = PreconditionsFormula(action = 'run',
                                       preconditions = ['step', 'walk'])

        expected_formula = '(! step_c | ! walk_c) -> ! run_a'

        self.assertEqual('sys_trans', formula.type)
        self.assertItemsEqual([expected_formula], formula.formulas)


class TSFormulaGenerationTests(unittest.TestCase):
    """Test the generation of Activation-Outcomes 'topology' formulas"""

    def setUp(self):
        """Gets called before every test case."""

        self.outcomes  = ['completed', 'failed']

        self.ts = {'r1': ['r1', 'r2', 'r3'],
                   'r2': ['r2'],
                   'r3': ['r3', 'r1']}

    def tearDown(self):
        """Gets called after every test case."""

        del self.outcomes
        del self.ts

    def test_bad_key_raises_exception(self):
        
        bad_ts = {100: ['ok_value']} # bad key, not str
        self.assertRaises(TypeError, ActivationOutcomesFormula,
                          sys_props = [], outcomes = ['completed'], ts = bad_ts)

    def test_bad_value_raises_exception(self):
        
        bad_ts = {'ok_key': 'bad_value'} # ok key, but value isn't a list
        self.assertRaises(TypeError, ActivationOutcomesFormula,
                          sys_props = [], outcomes = ['completed'], ts = bad_ts)

    def test_bad_values_raise_exception(self):
        
        bad_ts = {'ok_key': [100, 200]} # ok key, bad list elements are not str
        self.assertRaises(TypeError, ActivationOutcomesFormula,
                          sys_props = [], outcomes = ['completed'], ts = bad_ts)

    def test_value_not_in_keys_raises_exception(self):
        
        bad_ts = {'key_1': ['key_1', 'key_2']}
        self.assertRaises(ValueError, ActivationOutcomesFormula,
                          sys_props = [], outcomes = ['completed'], ts = bad_ts)

    def test_transition_system_conversion(self):
        
        formula = ActivationOutcomesFormula(sys_props = [], 
                                            outcomes = ['completed'],
                                            ts = self.ts)

        expected_ts = {'r1_c': ['r1_a', 'r2_a', 'r3_a'],
                       'r2_c': ['r2_a'],
                       'r3_c': ['r3_a', 'r1_a']}

        self.assertDictEqual(formula.ts, expected_ts)

    def test_sys_propositions_from_ts(self):
        
        formula = ActivationOutcomesFormula(sys_props = [], 
                                            outcomes = ['completed'],
                                            ts = self.ts)

        expected_sys_props = ['r1_a', 'r2_a', 'r3_a']

        self.assertItemsEqual(actual_seq =  formula.sys_props,
                              expected_seq = expected_sys_props)

    def test_env_propositions_from_ts(self):
        
        formula = ActivationOutcomesFormula(sys_props = [], 
                                            outcomes = ['completed'],
                                            ts = self.ts)

        expected_env_props = ['r1_c', 'r2_c', 'r3_c']

        self.assertItemsEqual(actual_seq =  formula.env_props,
                              expected_seq = expected_env_props)

    def test_topology_mutex_formula(self):
        
        formula = TopologyMutexFormula(self.ts)

        self.assertEqual('env_trans', formula.type)

        expected_formula_1 = 'next(r1_c) <-> (! next(r2_c) & ! next(r3_c))'
        expected_formula_2 = 'next(r2_c) <-> (! next(r1_c) & ! next(r3_c))'
        expected_formula_3 = 'next(r3_c) <-> (! next(r1_c) & ! next(r2_c))'

        expected_formulas = [expected_formula_1, expected_formula_2, expected_formula_3]

        self.assertItemsEqual(formula.formulas, expected_formulas)

    def test_transition_relation_formula(self):

        formula = TransitionRelationFormula(self.ts)

        self.assertEqual('sys_trans', formula.type)

        expected_formula_1 = 'next(r1_c) -> (next(r1_a & ! r2_a & ! r3_a) | ' + \
                                            'next(r2_a & ! r1_a & ! r3_a) | ' + \
                                            'next(r3_a & ! r1_a & ! r2_a) | ' + \
                                            'next(! r1_a & ! r2_a & ! r3_a))'
        expected_formula_2 = 'next(r2_c) -> (next(r2_a & ! r1_a & ! r3_a) | ' + \
                                            'next(! r1_a & ! r2_a & ! r3_a))'
        expected_formula_3 = 'next(r3_c) -> (next(r3_a & ! r1_a & ! r2_a) | ' + \
                                            'next(r1_a & ! r2_a & ! r3_a) | ' + \
                                            'next(! r1_a & ! r2_a & ! r3_a))'

        expected_formulas = [expected_formula_1, expected_formula_2, expected_formula_3]

        self.assertItemsEqual(formula.formulas, expected_formulas)

    def test_single_step_change_formula_with_one_outcome(self):

        formula = SingleStepChangeFormula(self.ts) # 'completed' used by default

        self.assertEqual('env_trans', formula.type)

        expected_formula_1a = '(r1_c & (r1_a & ! r2_a & ! r3_a)) -> next(r1_c)'
        expected_formula_1b = '(r1_c & (r2_a & ! r1_a & ! r3_a)) -> (next(r1_c) | next(r2_c))'
        expected_formula_1c = '(r1_c & (r3_a & ! r1_a & ! r2_a)) -> (next(r3_c) | next(r1_c))'
        expected_formula_2  = '(r2_c & (r2_a & ! r1_a & ! r3_a)) -> next(r2_c)'
        expected_formula_3a = '(r3_c & (r1_a & ! r2_a & ! r3_a)) -> (next(r3_c) | next(r1_c))'
        expected_formula_3b = '(r3_c & (r3_a & ! r1_a & ! r2_a)) -> next(r3_c)'

        expected_formulas = [expected_formula_1a, expected_formula_1b, expected_formula_1c,
                             expected_formula_2, expected_formula_3a, expected_formula_3b]

        self.assertItemsEqual(formula.formulas, expected_formulas)

    def test_single_step_change_formula_with_multiple_outcomes(self):
        
        formula = SingleStepChangeFormula(self.ts, ['completed', 'failed'])

        self.assertEqual('env_trans', formula.type)

        expected_formula_1a = '(r1_c & (r1_a & ! r2_a & ! r3_a)) -> (next(r1_c) | next(r1_f))'
        expected_formula_1b = '(r1_c & (r2_a & ! r1_a & ! r3_a)) -> (next(r1_c) | next(r2_f) | next(r2_c))'
        expected_formula_1c = '(r1_c & (r3_a & ! r1_a & ! r2_a)) -> (next(r3_c) | next(r3_f) | next(r1_c))'
        expected_formula_2  = '(r2_c & (r2_a & ! r1_a & ! r3_a)) -> (next(r2_f) | next(r2_c))'
        expected_formula_3a = '(r3_c & (r1_a & ! r2_a & ! r3_a)) -> (next(r3_c) | next(r1_c) | next(r1_f))'
        expected_formula_3b = '(r3_c & (r3_a & ! r1_a & ! r2_a)) -> (next(r3_c) | next(r3_f))'

        expected_formulas = [expected_formula_1a, expected_formula_1b, expected_formula_1c,
                             expected_formula_2, expected_formula_3a, expected_formula_3b]

        self.assertItemsEqual(formula.formulas, expected_formulas)

    def test_topology_outcome_constraint(self):
        
        formula = TopologyOutcomeConstraintFormula(self.ts, ['completed', 'failed'])

        self.assertEqual('env_trans', formula.type)

        expected_formula_1 = '(! r1_c & ! r1_a) -> next(! r1_c)'
        expected_formula_2 = '(! r2_c & ! r2_a) -> next(! r2_c)'
        expected_formula_3 = '(! r3_c & ! r3_a) -> next(! r3_c)'
        expected_formula_4 = '(! r1_f & ! r1_a) -> next(! r1_f)'
        expected_formula_5 = '(! r2_f & ! r2_a) -> next(! r2_f)'
        expected_formula_6 = '(! r3_f & ! r3_a) -> next(! r3_f)'

        expected_formulas = [expected_formula_1, expected_formula_2, expected_formula_3,
                             expected_formula_4, expected_formula_5, expected_formula_6]

        self.assertItemsEqual(formula.formulas, expected_formulas)

    def test_topology_outcome_persistence(self):
        
        formula = TopologyOutcomePersistenceFormula(self.ts, ['completed', 'failed'])

        self.assertEqual('env_trans', formula.type)

        expected_formula_1a = '(r1_c & (! r1_a & ! r2_a & ! r3_a)) -> next(r1_c)'
        expected_formula_1b = '(r1_f & (! r1_a & ! r2_a & ! r3_a)) -> next(r1_f)'
        expected_formula_2a = '(r2_c & (! r1_a & ! r2_a & ! r3_a)) -> next(r2_c)'
        expected_formula_2b = '(r2_f & (! r1_a & ! r2_a & ! r3_a)) -> next(r2_f)'
        expected_formula_3a = '(r3_c & (! r1_a & ! r2_a & ! r3_a)) -> next(r3_c)'
        expected_formula_3b = '(r3_f & (! r1_a & ! r2_a & ! r3_a)) -> next(r3_f)'

        expected_formulas = [expected_formula_1a, expected_formula_1b, expected_formula_2a,
                             expected_formula_2b, expected_formula_3a, expected_formula_3b]

        self.assertItemsEqual(formula.formulas, expected_formulas)

    def test_topology_fairness_conditions_single_outcome(self):
        
        formula = TopologyFairnessConditionsFormula(self.ts)

        self.assertEqual('env_liveness', formula.type)

        expected_formula_1a = '((r1_a & ! r2_a & ! r3_a) & next(r1_c))'
        expected_formula_1b = '((r2_a & ! r1_a & ! r3_a) & next(r2_c))'
        expected_formula_1c = '((r3_a & ! r1_a & ! r2_a) & next(r3_c))'
        expected_formula_1  = '(' + expected_formula_1a + ' | ' + \
                                    expected_formula_1b + ' | ' + \
                                    expected_formula_1c + ')' # completion
        
        expected_formula_2a = '((r1_a & ! r2_a & ! r3_a) & ! next(r1_a & ! r2_a & ! r3_a))'
        expected_formula_2b = '((r2_a & ! r1_a & ! r3_a) & ! next(r2_a & ! r1_a & ! r3_a))'
        expected_formula_2c = '((r3_a & ! r1_a & ! r2_a) & ! next(r3_a & ! r1_a & ! r2_a))'
        expected_formula_2  = '(' + expected_formula_2a + ' | ' + \
                                    expected_formula_2b + ' | ' + \
                                    expected_formula_2c + ')' # change
        
        expected_formula_3 = '(! r1_a & ! r2_a & ! r3_a)' # activate nothing

        expected_formula = '(' + expected_formula_1 + ' | ' + \
                                 expected_formula_2 + ' | ' + \
                                 expected_formula_3 + ')'

        self.assertItemsEqual([expected_formula], formula.formulas)

    def test_topology_fairness_conditions_with_outcomes(self):
        
        # self.fail('Incomplete test!')

        formula = TopologyFairnessConditionsFormula(
                                    ts = self.ts,
                                    outcomes = ['completed', 'failed'])

        self.assertEqual('env_liveness', formula.type)

        expected_formula_1a = '((r1_a & ! r2_a & ! r3_a) & (next(r1_c) | next(r1_f)))'
        expected_formula_1b = '((r2_a & ! r1_a & ! r3_a) & (next(r2_c) | next(r2_f)))'
        expected_formula_1c = '((r3_a & ! r1_a & ! r2_a) & (next(r3_c) | next(r3_f)))'
        expected_formula_1  = '(' + expected_formula_1a + ' | ' + \
                                    expected_formula_1b + ' | ' + \
                                    expected_formula_1c + ')' # completion
        
        expected_formula_2a = '((r1_a & ! r2_a & ! r3_a) & ! next(r1_a & ! r2_a & ! r3_a))'
        expected_formula_2b = '((r2_a & ! r1_a & ! r3_a) & ! next(r2_a & ! r1_a & ! r3_a))'
        expected_formula_2c = '((r3_a & ! r1_a & ! r2_a) & ! next(r3_a & ! r1_a & ! r2_a))'
        expected_formula_2  = '(' + expected_formula_2a + ' | ' + \
                                    expected_formula_2b + ' | ' + \
                                    expected_formula_2c + ')' # change (same)
        
        expected_formula_3 = '(! r1_a & ! r2_a & ! r3_a)' # activate nothing

        expected_formula = '(' + expected_formula_1 + ' | ' + \
                                 expected_formula_2 + ' | ' + \
                                 expected_formula_3 + ')'

        self.assertItemsEqual([expected_formula], formula.formulas)


class GoalFormulaGenerationTests(unittest.TestCase):
    """Test the generation of Activation-Outcomes liveness requirements"""

    def setUp(self):
        """Gets called before every test case."""

        self.sys_props = ['dance', 'sleep', 'swim']

    def tearDown(self):
        """Gets called after every test case."""

        del self.sys_props    

    def test_successful_outcome_formula(self):

        formula = SuccessfulOutcomeFormula(conditions = ['dance', 'sleep'],
                                           success = 'finished')

        self.assertEqual('sys_trans', formula.type)

        expected_sys_props = ['finished', 'dance_a', 'dance_m', 'sleep_a', 'sleep_m']
        self.assertItemsEqual(expected_sys_props, formula.sys_props)
        self.assertItemsEqual(['dance_c', 'sleep_c'], formula.env_props)

        expected_formula_0 = 'finished <-> (dance_m & sleep_m)'
        expected_formula_1 = 'next(dance_c) -> next(dance_m)'
        expected_formula_2 = 'dance_m -> next(dance_m)'
        expected_formula_3 = '(! dance_m & next(! dance_c)) -> next(! dance_m)'
        expected_formula_4 = 'next(sleep_c) -> next(sleep_m)'
        expected_formula_5 = 'sleep_m -> next(sleep_m)'
        expected_formula_6 = '(! sleep_m & next(! sleep_c)) -> next(! sleep_m)'

        expected_formulas = [expected_formula_0, expected_formula_1,
                             expected_formula_2, expected_formula_3,
                             expected_formula_4, expected_formula_5, expected_formula_6]

        self.assertItemsEqual(expected_formulas, formula.formulas)

    def test_strict_goal_ordering(self):

        formula = SuccessfulOutcomeFormula(conditions = ['dance', 'sleep', 'swim'],
                                           success = 'finished', strict_order = True)
        
        expected_formula_1 = '! dance_m -> next(! sleep_m)'
        expected_formula_2 = '! sleep_m -> next(! swim_m)'

        self.assertIn(expected_formula_1, formula.formulas)
        self.assertIn(expected_formula_2, formula.formulas)

    def test_failed_outcome_formula(self):

        formula = FailedOutcomeFormula(conditions = ['dance', 'sleep'],
                                       failure = 'failed')

        self.assertEqual('sys_trans', formula.type)

        expected_sys_props = ['failed', 'dance_a', 'sleep_a']
        self.assertItemsEqual(expected_sys_props, formula.sys_props)

        expected_env_props = ['dance_f', 'sleep_f']
        self.assertItemsEqual(expected_env_props, formula.env_props)

        expected_formula = 'next(failed) <-> ((next(dance_f) | next(sleep_f)) | failed)'

        self.assertItemsEqual([expected_formula], formula.formulas)

    def test_system_liveness_formula_single_goal(self):

        formula = SystemLivenessFormula(goals = ['finished'])

        self.assertEqual('sys_liveness', formula.type)

        self.assertItemsEqual(['finished'], formula.formulas)

    def test_system_liveness_formula_conjunction(self):

        formula = SystemLivenessFormula(goals = ['finished', '! failed'])

        self.assertEqual('sys_liveness', formula.type)

        self.assertItemsEqual(['(finished & ! failed)'], formula.formulas)

    def test_system_liveness_formula_disjunction(self):

        formula = SystemLivenessFormula(goals = ['finished', 'failed'],
                                        disjunction = True)

        self.assertEqual('sys_liveness', formula.type)

        self.assertItemsEqual(['(finished | failed)'], formula.formulas)


class ICFormulaGenerationTests(unittest.TestCase):
    """Test the generation of Activation-Outcomes initial condition formulas"""

    def setUp(self):
        """Gets called before every test case."""

        self.sys_props = ['dance', 'sleep', 'swim']

        self.ts = {'r1': ['r1', 'r2', 'r3'],
                   'r2': ['r2'],
                   'r3': ['r3', 'r1']}

    def tearDown(self):
        """Gets called after every test case."""

        del self.sys_props, self.ts

    def test_sys_init_from_true_actions(self):
        
        sys_props = ['dance_a', 'sleep_a', 'swim_a']
        true_props = ['dance', 'swim']
        formula = SystemInitialConditions(sys_props, true_props)

        self.assertEqual('sys_init', formula.type)
        self.assertItemsEqual(sys_props, formula.sys_props)
        self.assertItemsEqual(list(), formula.env_props)

        expected_formula = ['dance_a', 'swim_a', '! sleep_a']

        self.assertItemsEqual(expected_formula, formula.formulas)

    def test_env_init_from_true_actions(self):
        
        env_props = ['dance_c', 'sleep_c', 'swim_c',
                     'dance_f', 'sleep_f', 'swim_f']
        true_props = ['dance', 'swim']
        formula = EnvironmentInitialConditions(env_props, true_props)

        self.assertEqual('env_init', formula.type)
        self.assertItemsEqual(list(), formula.sys_props)
        self.assertItemsEqual(env_props, formula.env_props)

        expected_formula = ['dance_c', '! dance_f', 'swim_c', '! swim_f',
                            '! sleep_c', '! sleep_f']

        self.assertItemsEqual(expected_formula, formula.formulas)

# =============================================================================
# Entry point
# =============================================================================

if __name__ == '__main__':
    # Run all tests
    unittest.main()
