#!/usr/bin/env python

from gr1_specification import GR1Specification
from ..formula import *

"""
Module's docstring #TODO

* Generate formulas
* Load formulas in specification

"""

class TransitionSystemSpecification(GR1Specification):
    """
    docstring for TransitionSystemSpecification

    Arguments:
      ts    dict    Dictionary encoding a transition system (TS).

    """
    def __init__(self, name = '', ts = {}, 
                 props_of_interest = [], 
                 outcomes = ['completed']):
        super(TransitionSystemSpecification, self).__init__(spec_name = name,
                                                            env_props = [],
                                                            sys_props = [])
        
        self.ts = self._get_ts_of_interest(ts, props_of_interest)
        self._prepare_formulas_from_ts(act_out = True, outcomes = outcomes)

    def _prepare_formulas_from_ts(self, act_out = True,
                                  outcomes = ['completed']):
        
        if act_out:
            formulas_from_ts = self._gen_act_out_topology_formulas(outcomes)
        else:
            raise NotImplementedError('TS formulas for the vanilla GR(1) ' +
                                      'paradigm have not been implemented yet!')
        
        # Finally, load the formulas (and props) into the GR1 Specification
        self.load_formulas(formulas_from_ts)

    def _gen_act_out_topology_formulas(self, outcomes):

        trans_relation_formula = TransitionRelationFormula(ts = self.ts)
        topology_mutex_formula = TopologyMutexFormula(ts = self.ts)
        single_step_formula = SingleStepChangeFormula(
                                            ts = self.ts,
                                            outcomes = outcomes)
        persistence_formula = TopologyOutcomePersistenceFormula(
                                            ts = self.ts,
                                            outcomes = outcomes)
        fairness_condition = TopologyFairnessConditionsFormula(
                                            ts = self.ts,
                                            outcomes = outcomes)
        constraints_formula = TopologyOutcomeConstraintFormula(
                                            ts = self.ts,
                                            outcomes = outcomes)
        mutex_formula = OutcomeMutexFormula(sys_props = self.ts.keys(),
                                            outcomes = outcomes)
        deactivation_formula = PropositionDeactivationFormula(
                                            sys_props = self.ts.keys(),
                                            outcomes = outcomes)

        topology_formulas = [trans_relation_formula, topology_mutex_formula,
                             single_step_formula, persistence_formula,
                             fairness_condition, constraints_formula, 
                             mutex_formula, deactivation_formula]

        return topology_formulas

    @staticmethod
    def _get_ts_of_interest(original_ts, props_of_interest):
        """..."""

        if not props_of_interest:
            ts = original_ts
        else:
            ts = dict()
            for pi in props_of_interest:
                # Cherry-pick the props of interest from the dictionary
                transitions = original_ts[pi]
                ts[pi] = [t for t in transitions if t in props_of_interest]
        return ts
