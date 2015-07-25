#!/usr/bin/env python

from gr1_specification import GR1Specification
from ..formula import *

"""
Module's docstring #TODO
"""


class GoalSpecification(GR1Specification):
    """
    A specificaton containing formulas that encode the conditions under which 
    the system/robot wins. Includes both safety and livenesss requirements.
    """
    
    def __init__(self, name = ''):
        super(GoalSpecification, self).__init__(spec_name = name,
                                                env_props = [],
                                                sys_props = [])

    def handle_single_liveness(self, goals, outcomes = ['finished']):
        """
        Create a single system liveness requirement (e.g. []<> finished) 
        from one or more goals. The method also generates the necessary 
        formulas for triggerring the liveness(es).
        """

        goal_formulas = list()

        #TODO: Refactor the hacky handling of outcomes below
        if len(outcomes) == 0:
            raise NotImplementedError('Cannot handle zero outcomes yet!') #FIX
        else: # Assumes that the first outcome is success
            liveness_formula = SystemLivenessFormula(goals = outcomes,
                                                     disjunction = True)
            success_formula = SuccessfulOutcomeFormula(conditions = goals,
                                                       success = outcomes[0])     
            goal_formulas.extend([liveness_formula, success_formula])
        
        if len(outcomes) > 2:
            raise NotImplementedError('Only success and failure are supported!')

        # Finally, load the formulas (and props) into the GR1 Specification
        self.load_formulas(goal_formulas)

    def handle_liveness_conjunction(self):
        #TODO: Handle liveness requirements of the form []<> (a & b)
        pass

    def handle_any_failure(self, conditions, failure = 'failed'):
        
        failure_formula = FailedOutcomeFormula(conditions, failure)

        self.load(failure_formula)
