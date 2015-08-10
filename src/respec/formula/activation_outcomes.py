#!/usr/bin/env python

from ..ltl import ltl as LTL
from gr1_formulas import GR1Formula

"""
The activation-outcomes paradigm generalizes the activation-completion paradigm
in Vasumathi Raman and Hadas Kress-Gazit (ICRA 2013).

The base class ActivationOutcomesFormula is a generalization of FastSlowFormula.

"""

class ActivationOutcomesFormula(GR1Formula):
    """
    
    Arguments:
      sys_props (list of str)   System propositions (strings)
      outcomes  (list of str)   The possible outcomes of activating actions.
                                Example: ['completed', 'failed', 'preempted']
                                Defaults to the singleton ['completed']
                                Ideally, the first character of outcomes will
                                be unique, such as in the example above (c,f,p)
      ts        (dict of str)   Transition system, TS (e.g. workspace topology)
                                Implicitly contains some props in its keys.

    Attributes:
      outcomes   (list of str)  The possible outcomes of activating a prop.
      outcome_props (dict of str)   The propositions corresponding
                                    to each possible activation outcome.
      ts        (dict of str)   The input TS but transformed such that the keys
                                are completion props and the values activation.

    Raises:
      TypeError
      ValueError
    
    """

    def __init__(self, sys_props, outcomes = ['completed'], ts = dict()):

        # Check whether the input arguments are of the correct type, etc.
        self._check_input_arguments(sys_props, outcomes, ts)
        
        self.outcomes = outcomes

        sys_props = sys_props + ts.keys()

        # Generate activation (list) and outcome (dict) propositions
        act_props = map(_get_act_prop, sys_props)
        self.outcome_props = self._gen_outcome_propositions(sys_props)
        # Get the outcome props (environment) as a list
        env_props = self._get_env_props_from_outcome_props()

        super(ActivationOutcomesFormula, self).__init__(env_props = env_props,
                                                        sys_props = act_props,
                                                        ts = {}) # bypass ts

        # Convert the transition system's props to activation-outcome props
        #TODO: Not really useful besides for TransitionRelation formula [?]
        self.original_ts = ts
        self.ts = self._convert_ts_to_act_out(ts) # overwrites self.ts

    def _check_input_arguments(self, sys_props, outcomes, ts):
        """Check type of input arguments as well as adherence to conventions."""

        if any([type(pi) != str for pi in sys_props]):
            raise TypeError('Invalid type of system props (expected str): {}'
                            .format(map(type, sys_props)))

        if any([_is_activation(pi) for pi in sys_props]):
            raise ValueError('Invalid system props (already activation): {}'
                            .format(sys_props))

        if not outcomes:
            raise ValueError('No outcomes where provided! ' +
                             'At least "completed" (or equivalent) is required.')

        if any([type(out) != str for out in outcomes]):
            raise TypeError('Invalid type of outcomes (expected str): {}'
                            .format(map(type, outcomes)))

        # Check convention of outcome names
        out_first_chars = [out[0] for out in outcomes]
        if any([True for c in out_first_chars if out_first_chars.count(c) > 1]):
            raise ValueError('The outcomes do not adhere to the convention ' +
                             'that their first character is unique: {}'
                             .format(outcomes))

        # Check that the TS dictionary is well-formed: {str: list of str}
        if any([type(k) is not str for k in ts.keys()]):
            raise TypeError('Invalid type of TS key props (expected str): {}'
                            .format(map(type, ts.keys())))
        if any([type(v) is not list for v in ts.values()]):
            raise TypeError('Invalid type of TS dict values (expected list): {}'
                            .format(map(type, ts.values())))
        
        all_values = reduce(lambda acc, ele: acc + ele, ts.values(), [])
        
        if any([type(v) is not str for v in all_values]):
            raise TypeError('Invalid type of TS value props (expected str): {}'
                            .format(map(type, all_values)))

        if any([v not in ts.keys() for v in all_values]):
            raise ValueError('Some values are not in the keys of the TS: {}'
                             .format(all_values))

    def _gen_outcome_propositions(self, sys_props):
        """
        For each system proposition (action, region ,etc.), 
        create the corresponding outcome propositions (e.g. completion).      
        """

        outcome_props = dict()
        for pi in sys_props:       
            outcome_props[pi] = [_get_out_prop(pi,out) for out in self.outcomes]
        return outcome_props

    def _get_env_props_from_outcome_props(self):
        """Collect all the outcome propositions in one list."""

        env_props = reduce(lambda acc, ele: acc + ele,
                           self.outcome_props.values(), [])
        return env_props

    @staticmethod
    def _convert_ts_to_act_out(ts):
        """Convert the keys to completion props and the values to activation."""
        
        new_ts = dict()
        for k in ts.keys():        
            k_c = _get_com_prop(k)                  # completion prop
            k_c_values = map(_get_act_prop, ts[k])  # activation props
            new_ts[k_c] = k_c_values
        return new_ts


class OutcomeMutexFormula(ActivationOutcomesFormula):
    """The outcomes of an action are mutually exclusive."""
    
    def __init__(self, sys_props, outcomes):
        super(OutcomeMutexFormula, self).__init__(sys_props = sys_props,
                                                  outcomes = outcomes)

        if len(outcomes) == 1:
            print('No need for OutcomeMutex for: ' +
                  '{0} Only one outcome found: {1}'
                  .format(sys_props, outcomes))
        else:
            self.formulas = self._gen_outcome_mutex_formulas()
        
        self.type = 'env_trans'

    def _gen_outcome_mutex_formulas(self):
        """Generate the formulas establishing mutual exclusion."""
        
        mutex_formulas = list()

        for pi in self.outcome_props.keys():

            # Use the method of the parent's parent class (GR1Formula)
            pi_outs = self.outcome_props[pi]
            formulas = self._gen_single_mutex_formulas(pi_outs)
            mutex_formulas.extend(formulas)

        return mutex_formulas

    def _gen_single_mutex_formulas(self, outcome_props):
        
        formulas = list()

        for prop in outcome_props:
            other_props = [p for p in outcome_props if p != prop]
            
            next_neg_props = map(LTL.next, map(LTL.neg, other_props))

            right_hand_side = LTL.conj(next_neg_props)
            
            formulas.append(LTL.implication(left_hand_side = LTL.next(prop),
                                            right_hand_side = right_hand_side))

        return formulas


class ActionOutcomeConstraintsFormula(ActivationOutcomesFormula):
    """Safety formulas that constrain the outcomes of actions."""

    def __init__(self, actions, outcomes = ['completed']):
        super(ActionOutcomeConstraintsFormula, self).__init__(sys_props = actions,
                                                              outcomes = outcomes)
        
        self.formulas = self._gen_action_outcomes_formulas()
        self.type = 'env_trans'

    def _gen_action_outcomes_formulas(self):
        """Equivalent of Equations (3) and (4)"""

        eq3_formulas = list()
        eq4_formulas = list()

        for pi in self.outcome_props.keys():

            pi_a = _get_act_prop(pi)
            pi_outcomes = self.outcome_props[pi]

            # Generate Eq. (3)
            lhs_disjunct = LTL.disj(pi_outcomes)
            left_hand_side = LTL.conj([lhs_disjunct, pi_a])

            rhs_props = map(LTL.next, pi_outcomes)
            right_hand_side = LTL.disj(rhs_props)
            
            formula = LTL.implication(left_hand_side, right_hand_side)
            eq3_formulas.append(formula)

            # Generate Eq. (4)
            not_pi_a = LTL.neg(pi_a)

            for pi_out in pi_outcomes:
                
                not_pi_out = LTL.neg(pi_out)
                left_hand_side = LTL.conj([not_pi_out, not_pi_a])
                right_hand_side = LTL.next(not_pi_out)
                
                formula = LTL.implication(left_hand_side, right_hand_side)
                eq4_formulas.append(formula)

        return eq3_formulas + eq4_formulas


class ActionOutcomePersistenceFormula(ActivationOutcomesFormula):
    """
    Formulas that force action outcomes to persist if they are not reactivated.
    """

    def __init__(self, actions, outcomes = ['completed']):
        super(ActionOutcomePersistenceFormula, self).__init__(sys_props = actions,
                                                              outcomes = outcomes)
        
        self.formulas = self._gen_outcome_persistence_formulas()
        self.type = 'env_trans'

    def _gen_outcome_persistence_formulas(self):
        """New in activation-deactivation paradigm."""

        persistence_formulas = list()

        for pi in self.outcome_props.keys():

            pi_a = _get_act_prop(pi)
            pi_outcomes = self.outcome_props[pi]
            not_pi_a = LTL.neg(pi_a)

            for pi_out in pi_outcomes:

                left_hand_side = LTL.conj([pi_out, not_pi_a])
                formula = LTL.implication(left_hand_side, LTL.next(pi_out))
                persistence_formulas.append(formula)

        return persistence_formulas


class PropositionDeactivationFormula(ActivationOutcomesFormula):
    """
    Turn action proposition OFF once an outcome is returned.
    """
    
    def __init__(self, sys_props, outcomes = ['completed']):
        super(PropositionDeactivationFormula, self).__init__(sys_props = sys_props,
                                                             outcomes = outcomes)

        self.formulas = self._gen_proposition_deactivation_formulas()
        self.type = 'sys_trans'

    def _gen_proposition_deactivation_formulas(self):
        """
        Generate a safety requirement that turns an activation proposition
        off once a corresponding action outcome has become True.
        """

        deactivation_formulas = list()

        for pi in self.outcome_props.keys():

            pi_outs = self.outcome_props[pi]
            next_pi_outs = map(LTL.next, pi_outs)
            out_disjunct = LTL.disj(next_pi_outs)

            pi_a = _get_act_prop(pi)
            next_not_pi_a = LTL.next(LTL.neg(pi_a))

            left_hand_side = LTL.conj([pi_a, out_disjunct])

            formula = LTL.implication(left_hand_side, next_not_pi_a)
            deactivation_formulas.append(formula)

        return deactivation_formulas

class ActionFairnessConditionsFormula(ActivationOutcomesFormula):
    """
    Environment liveness formulas that ensure that every action proposition (not
    topology) eventually returns an outcome (or that the robot changes its mind)
    
    Arguments:
      mutex    (bool)   Whether the action props are mutually exclusive or not

    """

    def __init__(self, actions, outcomes = ['completed'], mutex = False):
        super(ActionFairnessConditionsFormula, self).__init__(sys_props = actions,
                                                              outcomes = outcomes)
        
        self.formulas = self._gen_action_fairness_formulas()
        self.type = 'env_liveness'

    def _gen_action_fairness_formulas(self):
        """Fairness conditions (for actions) from Section V-B (4)"""

        #TODO: Be more efficient if props are mutually exclusive

        fairness_formulas = list()

        for pi in self.outcome_props.keys():

            pi_a = _get_act_prop(pi)
            not_pi_a = LTL.neg(pi_a)
            pi_outcomes = self.outcome_props[pi]

            next_pi_outs = map(LTL.next, pi_outcomes)
            out_disjunct = LTL.disj(next_pi_outs)
            next_not_pi_outs = map(LTL.next, map(LTL.neg, pi_outcomes))
            out_conjunct = LTL.conj(next_not_pi_outs)
            
            outcomes_disjunct_1 = LTL.conj([pi_a, out_disjunct])
            outcomes_disjunct_2 = LTL.conj([not_pi_a, out_conjunct])
            outcomes_disjunct_3 = LTL.conj([not_pi_a, out_disjunct])
            outcomes_formula = LTL.disj([outcomes_disjunct_1,
                                         outcomes_disjunct_2,
                                         outcomes_disjunct_3])

            change_disjunt_1 = LTL.conj([pi_a, LTL.next(not_pi_a)])
            change_disjunt_2 = LTL.conj([not_pi_a, LTL.next(pi_a)])
            change_formula = LTL.disj([change_disjunt_1, change_disjunt_2])

            fairness_condition = LTL.disj([outcomes_formula, change_formula])

            fairness_formulas.append(fairness_condition)

        return fairness_formulas


class PreconditionsFormula(GR1Formula):
    """The outcomes of an action are mutually exclusive."""
    
    def __init__(self, action, preconditions):

        action_prop = _get_act_prop(action)
        pc_props = map(_get_com_prop, preconditions)

        super(PreconditionsFormula, self).__init__(env_props = pc_props,
                                                   sys_props = [action_prop])

        self.formulas = [self.gen_precondition_formula(action_prop,
                                                       pc_props)]
        self.type = 'sys_trans'

# =============================================================================
# Topology-specific formulas (i.e., those based on a transition system encoding)
# =============================================================================

class TransitionRelationFormula(ActivationOutcomesFormula):
    """
    Generate system requirement formulas that
    encode the transition system (e.g. workspace topology).

    The transition system TS, is provided in the form of a dictionary.
    """
    
    def __init__(self, ts):
        super(TransitionRelationFormula, self).__init__(sys_props = [],
                                                        ts = ts)

        self.formulas = self._gen_system_transition_relation_formulas(ts)
        self.type = 'sys_trans'

    def _gen_system_transition_relation_formulas(self, ts):
        """
        Safety requirements from Section V-B (2), but extended with the 
        option to not activate any proposition in the next time step.
        """

        activate_nothing = _get_act_nothing(ts.keys())

        sys_trans_formulas = list()
        for prop in ts.keys():
            left_hand_side = LTL.next(_get_com_prop(prop))
            right_hand_side = list()
            
            for adj_prop in ts[prop]:
                adj_prop_a = _get_act_prop(adj_prop)
                adj_phi_prop = self._gen_phi_prop(adj_prop_a)
                disjunct = LTL.next(adj_phi_prop)
                right_hand_side.append(disjunct)

            activate_nothing_disjunct = LTL.next(activate_nothing)
            right_hand_side.append(activate_nothing_disjunct)
            
            right_hand_side = LTL.disj(right_hand_side)
            sys_trans_formulas.append(LTL.implication(left_hand_side,
                                                      right_hand_side))

        return sys_trans_formulas


class TopologyMutexFormula(ActivationOutcomesFormula):
    """
    Generate environment assumptions/constraints that enforce 
    mutual exclusion between the topology propositions; Eq. (1)

    The transition system TS, is provided in the form of a dictionary.
    """
    
    def __init__(self, ts):
        super(TopologyMutexFormula, self).__init__(sys_props = [],
                                                   outcomes = ['completed'],
                                                   ts = ts)
        
        # Delegate to the parent's parent class (GR1Formula) method
        self.formulas = self.gen_mutex_formulas(self.env_props, future = True)
        self.type = 'env_trans'


class SingleStepChangeFormula(ActivationOutcomesFormula):
    """
    Safety formulas that govern how the topology propositions can change
    in a single time step in response to activation propositions.

    If no outcomes (besides 'completed') are provided, the transition system
    will be used instead (e.g. ending up in a different region than expected).
    If they are provided, those outcomes will be used in the formulas
    (e.g. failed to transition to the next region).
    """

    def __init__(self, ts, outcomes = ['completed']):
        super(SingleStepChangeFormula, self).__init__(sys_props = [],
                                                      outcomes = outcomes,
                                                      ts = ts)
        
        self.formulas = self._gen_single_step_change_formulas(ts)
        self.type = 'env_trans'

    def _gen_single_step_change_formulas(self, ts):
        """Equivalent of Eq. (2)"""
        
        all_formulas = list()

        for pi in ts.keys():
            
            pi_c = _get_com_prop(pi)
            next_pi_c = LTL.next(pi_c)
            
            for pi_prime in ts[pi]:
                
                pi_prime_a = _get_act_prop(pi_prime)
                phi = self._gen_phi_prop(pi_prime_a)

                left_hand_side = LTL.conj([pi_c, phi])

                act_outcomes = map(LTL.next, self.outcome_props[pi_prime])
                
                rhs_elements = [next_pi_c] # reinitialize list for new pi_prime
                rhs_elements.extend(act_outcomes)
                rhs_elements = list(set(rhs_elements)) # clear duplicates

                right_hand_side = LTL.disj(rhs_elements)

                implication = LTL.implication(left_hand_side, right_hand_side)

                all_formulas.append(implication)

        return all_formulas


class TopologyOutcomeConstraintFormula(ActivationOutcomesFormula):
    """Safety formulas that constrain the outcomes of topology transitions."""

    def __init__(self, ts, outcomes = ['completed']):
        super(TopologyOutcomeConstraintFormula, self).__init__(
                                                        sys_props = [],
                                                        outcomes = outcomes,
                                                        ts = ts)
        
        self.formulas = self._gen_topology_outcomes_formulas(ts)
        self.type = 'env_trans'

    def _gen_topology_outcomes_formulas(self, ts):
        """Equivalent of Equation (4)"""

        eq4_formulas = list()

        for pi in ts.keys():

            pi_a = _get_act_prop(pi)
            pi_outcomes = self.outcome_props[pi]

            # Generate Eq. (4)
            not_pi_a = LTL.neg(pi_a)

            for pi_out in pi_outcomes:
                
                not_pi_out = LTL.neg(pi_out)
                left_hand_side = LTL.conj([not_pi_out, not_pi_a])
                right_hand_side = LTL.next(not_pi_out)
                
                formula = LTL.implication(left_hand_side, right_hand_side)
                eq4_formulas.append(formula)

        return eq4_formulas


class TopologyOutcomePersistenceFormula(ActivationOutcomesFormula):
    """
    Formulas that force topology transitions outcomes to persist
    while no topology transitions are being activated.
    """

    def __init__(self, ts, outcomes = ['completed']):
        super(TopologyOutcomePersistenceFormula, self).__init__(sys_props = [],
                                                                outcomes = outcomes,
                                                                ts = ts)
        
        self.formulas = self._gen_topo_outcome_persistence_formulas(ts)
        self.type = 'env_trans'

    def _gen_topo_outcome_persistence_formulas(self ,ts):
        """
        New due to multiple outcomes of a topological transition and
        also due to the activation-deactivation paradigm."""

        persistence_formulas = list()

        activate_nothing = _get_act_nothing(ts.keys())

        for pi in ts.keys():
            
            pi_outcomes = self.outcome_props[pi]

            for pi_out in pi_outcomes:

                left_hand_side = LTL.conj([pi_out, activate_nothing])
                formula = LTL.implication(left_hand_side, LTL.next(pi_out))
                persistence_formulas.append(formula)

        return persistence_formulas


class TopologyFairnessConditionsFormula(ActivationOutcomesFormula):
    """
    Environment liveness formulas that ensure that every transition on the
    TS eventually returns an outcome (or that the robot changes its mind).
    The possible outcomes are all adjacent states in the transition system.
    """

    def __init__(self, ts, outcomes = ['completed']):
        super(TopologyFairnessConditionsFormula, self).__init__(
                                        sys_props = [],
                                        outcomes = outcomes,
                                        ts = ts)
        
        self.formulas = self._gen_ts_fairness_formulas(ts)
        self.type = 'env_liveness'

    def _gen_ts_fairness_formulas(self, ts):
        """Fairness conditions (for regions) from Section V-B (4)"""
        
        completion_terms = list()
        change_terms = list()

        for pi in ts.keys():

            pi_a = _get_act_prop(pi)
            phi = self._gen_phi_prop(pi_a)

            not_next_phi = LTL.neg(LTL.next(phi))

            pi_outcomes = self.outcome_props[pi]
            next_pi_outs = map(LTL.next, pi_outcomes)
            out_disjunct = LTL.disj(next_pi_outs)

            completion_term = LTL.conj([phi, out_disjunct])
            completion_terms.append(completion_term)
            
            change_term = LTL.conj([phi, not_next_phi])
            change_terms.append(change_term)

        completion_formula = LTL.disj(completion_terms)
        change_formula = LTL.disj(change_terms)
        activate_nothing = _get_act_nothing(ts.keys())
        fairness_formula = LTL.disj([completion_formula,
                                     change_formula,
                                     activate_nothing])

        return [fairness_formula]


# =============================================================================
# System liveness requirements (including memory formulas)
# =============================================================================

class SystemLivenessFormula(ActivationOutcomesFormula):
    """
    ...
    """

    def __init__(self, goals, disjunction = False):
        super(SystemLivenessFormula, self).__init__(sys_props = [])

        #TODO: Add methods and input arg for also handling disjunction
        # It's necessary for handling failure: []<> (finished | failed)
        self.formulas = self._gen_liveness_formula(goals, disjunction)

        self.type = 'sys_liveness'

    def _gen_liveness_formula(self, goals, disjunction):
        #TODO: Move to gr1_formulas [?]
        
        liveness_formula = LTL.disj(goals) if disjunction else LTL.conj(goals)

        return [liveness_formula]


class SuccessfulOutcomeFormula(ActivationOutcomesFormula):
    """
    System requirement for activating the successful outcome of the state
    machine once all of the conditions have been met.
    """

    def __init__(self, conditions, success = 'finished', strict_order = False):
        super(SuccessfulOutcomeFormula, self).__init__(sys_props = conditions)

        memory_props = list()

        for goal in conditions:
            successful_outcome = _get_com_prop(goal) # Assume completion
            memory_prop = self._gen_memory_prop(goal)
            memory_props.append(memory_prop)
        
            memory_formula = self._gen_memory_formulas(mem_prop = memory_prop, 
                                                       goal = successful_outcome)
            self.formulas.extend(memory_formula)

        if strict_order:
            order_formulas = self._gen_goal_ordering_formulas(memory_props)
            self.formulas.extend(order_formulas)

        self.sys_props.append(success)

        success_condition = self.gen_success_condition(memory_props, success)

        self.formulas.append(success_condition)

        self.type = 'sys_trans'

    def _gen_memory_formulas(self, mem_prop, goal):
        '''
        For a proposition corresponding to a desired objective, creates a memory
        proposition and formulas for remembering achievement of that objective.
        '''

        set_mem_formula = LTL.implication(LTL.next(goal), LTL.next(mem_prop))
        remembrance_formula = LTL.implication(mem_prop, LTL.next(mem_prop))
        precondition = LTL.conj([LTL.neg(mem_prop), LTL.next(LTL.neg(goal))])
        guard_formula = LTL.implication(precondition, LTL.next(LTL.neg(mem_prop)))

        goal_memory_formulas = [set_mem_formula,
                                remembrance_formula,
                                guard_formula]

        return goal_memory_formulas

    def _gen_goal_ordering_formulas(self, memory_props):
        '''...'''

        strict_goal_order_formulas = list()

        for i in range(1, len(memory_props)):

            left_hand_side = LTL.neg(memory_props[i-1])
            right_hand_side = LTL.next(LTL.neg((memory_props[i])))
            memory_pair = LTL.implication(left_hand_side, right_hand_side)
            strict_goal_order_formulas.append(memory_pair)

        return strict_goal_order_formulas

    def _gen_memory_prop(self, prop):
        '''
        Creates a memory proposition from the given proposition
        and adds the memory proposition to the system propositions.
        '''

        mem_prop = prop + '_m'

        self.sys_props.append(mem_prop)

        return mem_prop

class FailedOutcomeFormula(ActivationOutcomesFormula):
    """
    System requirement for activating the failure outcome of the state
    machine once any of the conditions has been met.
    """

    def __init__(self, conditions, failure = 'failed'):
        super(FailedOutcomeFormula, self).__init__(sys_props = conditions,
                                                   outcomes = [failure])

        self.sys_props.append(failure)

        self.formulas = self._gen_failure_condition_formula(failure)

        self.type = 'sys_trans'

    def _gen_failure_condition_formula(self, failure):
        """Failure if and only if any of the conditions are met."""

        conditions = LTL.disj(map(LTL.next, self.env_props))

        disjunction = LTL.disj([conditions, failure])

        failure_condition = LTL.iff(LTL.next(failure), disjunction)

        return [failure_condition]
    

# =============================================================================
# System and environment initial condition formulas
# =============================================================================

class SystemInitialConditions(GR1Formula):
    """..."""
    
    def __init__(self, sys_props, true_props):
        super(SystemInitialConditions, self).__init__(sys_props = sys_props)
        
        self.formulas = self._gen_sys_init_from_true_props(sys_props,true_props)    
        
        self.type = 'sys_init'

    def _gen_sys_init_from_true_props(self, sys_props, true_props):
        
        sys_init_props = list()

        for pi_a in sys_props:

            if pi_a in map(_get_act_prop, true_props):
                sys_init_props.append(pi_a)
            else:
                not_pi_a = LTL.neg(pi_a)
                sys_init_props.append(not_pi_a)

        return sys_init_props

class EnvironmentInitialConditions(GR1Formula):
    """..."""

    def __init__(self, env_props, true_props):
        super(EnvironmentInitialConditions, self).__init__(env_props=env_props)
        
        self.formulas = self._gen_env_init_from_true_props(env_props,true_props) 
        
        self.type = 'env_init'

    def _gen_env_init_from_true_props(self, env_props, true_props):
        
        env_init_props = list()

        for pi_out in env_props:

            if pi_out in map(_get_com_prop, true_props):
                env_init_props.append(pi_out)
            else:
                not_pi_out = LTL.neg(pi_out)
                env_init_props.append(not_pi_out)

        return env_init_props

# =============================================================================
# Module-level helper functions
# =============================================================================

def _get_act_nothing(props):
    """Conjunction stands for not activating any of the activation props."""
    return LTL.conj(map(LTL.neg, map(_get_act_prop, props)))

def _get_act_prop(prop):
    if _is_activation(prop):
        raise ValueError('Activation prop was requested for {}!'.format(prop))
    else:
        return prop + "_a" # 'a' stands for activation

def _get_com_prop(prop):
    # Still necessary due to preconditions and topology formulas
    return _get_out_prop(prop, 'completed')

def _get_out_prop(prop, outcome):
    # If an activation proposition was passed, strip the '_a' suffix
    if _is_activation(prop):
        prop = prop[:-2]
    # Use first character of the outcome's name (string) as the subscript
    return prop + "_" + outcome[0]

def _is_activation(prop):
    return prop[-2:] == "_a"

# =========================================================
# Entry point
# =========================================================

def main(): #pragma: no cover
    
    formulas  = list()
    sys_props = ['dance', 'sleep']
    outcomes  = ['completed', 'failed', 'preempted']

    ts = {'r1' : ['r2'], 'r2': ['r1']}

    formulas.append(OutcomeMutexFormula(sys_props, outcomes))

    formulas.append(ActionOutcomeConstraintsFormula(sys_props, outcomes))

    formulas.append(PropositionDeactivationFormula(sys_props, outcomes))

    formulas.append(ActionFairnessConditionsFormula(sys_props, outcomes))

    for formula in formulas:
        print '---'
        print 'Formula Class:\t',   formula.__class__.__name__ # prints class name
        print 'GR(1) Type:\t',      formula.type
        print 'System props:\t',    formula.sys_props
        print 'Env props:\t',       formula.env_props
        print 'Outcomes:\t',        formula.outcome_props
        print 'Formula(s):\t',      formula.formulas

if __name__ == "__main__": #pragma: no cover
    main()
