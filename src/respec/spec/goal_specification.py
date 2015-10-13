#!/usr/bin/env python

from gr1_specification import GR1Specification
from ..formula import *

"""
Module's docstring #TODO
"""

SM_OUTCOME_SUCCESS = 'finished'
SM_OUTCOME_FAILURE = 'failed'

class GoalSpecification(GR1Specification):
    """
    A specificaton containing formulas that encode the conditions under which 
    the system/robot wins. Includes both safety and livenesss requirements.
    """
    
    def __init__(self, name = ''):
        super(GoalSpecification, self).__init__(spec_name = name,
                                                env_props = [],
                                                sys_props = [])

    def handle_single_liveness(self, goals,
                               outcomes = ['finished'], strict_order = False):
        """
        Create a single system liveness requirement (e.g. []<> finished) 
        from one or more goals. The method also generates the necessary 
        formulas for triggerring the liveness(es).
        """

        goal_formulas = list()

        #TODO: Refactor the hacky handling of outcomes below
        if len(outcomes) == 0:
            raise NotImplementedError('Cannot handle zero outcomes yet!') #FIX
        elif len(outcomes) > 2:
            raise NotImplementedError('Only success and failure are supported!')
        
        elif len(outcomes) == 1 and outcomes[0] == SM_OUTCOME_FAILURE:
            
            for goal in goals:
                liveness_formula = SimpleLivenessRequirementActOutFormula(
                                                goal = goal,
                                                sm_outcome = SM_OUTCOME_FAILURE)
                goal_formulas.append(liveness_formula)
        
        # elif len(outcomes) == 1 and outcomes[0] == SM_OUTCOME_SUCCESS:
        
        else:
            liveness_formula = SimpleLivenessRequirementFormula(
                                                goals = outcomes,
                                                disjunction = True)
            success_formula = SuccessfulOutcomeFormula(
                                                conditions = goals,
                                                success = SM_OUTCOME_SUCCESS,
                                                strict_order = strict_order)
            goal_formulas.extend([liveness_formula, success_formula])
                

        # Finally, load the formulas (and props) into the GR1 Specification
        self.load_formulas(goal_formulas)

    def handle_liveness_conjunction(self):
        #TODO: Handle liveness requirements of the form []<> (a & b)
        pass

    def handle_any_failure(self, conditions, failure = 'failed'):
        
        failure_formula = FailedOutcomeFormula(conditions, failure)

        self.load(failure_formula)

    def handle_retry_after_failure(self, failures):
        
        # retry_formula = RetryAfterFailureFormula(failures = failures)

        # eventual_completion_formula = ActivationEventuallyCompletesFormula(
        #                                                     actions = failures)

        eventual_completion_formula = ActionFairnessConditionsFormula(
                                                    actions = failures,
                                                    outcomes = ['completed'])

        self.load_formulas([eventual_completion_formula])
