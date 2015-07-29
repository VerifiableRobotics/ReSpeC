#!/usr/bin/env python

from respec.spec import *

"""
The module defines the components that make up a LTL specification for ATLAS.

The name of the class below, CompleteSpecification, should be the same for all
robots to facilitate integration with ROS. Only the module's name and the 
details of the class's constructor should change between robots.
"""

SM_OUTCOME_SUCCESS = 'finished'
SM_OUTCOME_FAILURE = 'failed'

class CompleteSpecification(GR1Specification):
    """
    Upon construction, this class generates LTL specifications for individual
    subcomponents of ATLAS (BDI control mode transition system, action 
    preconditions) as well as LTL specifications for the objective and the 
    initial conditions. It then merges them onto the object itself.
    """
    
    def __init__(self, name, initial_conditions, goals,
                 action_outcomes = ['completed', 'failed'],
                 sm_outcomes = [SM_OUTCOME_SUCCESS, SM_OUTCOME_FAILURE],
                 strict_order = True):
        
        super(CompleteSpecification, self).__init__(spec_name = name,
                                                    env_props = [],
                                                    sys_props = [])

        self._check_input_arguments(initial_conditions, goals,
                                    action_outcomes, sm_outcomes)

        # Load control modes and action preconditions from config file
        atlas_config = RobotConfiguration('atlas')
        control_mode_ts = atlas_config.ts
        atlas_preconditions = atlas_config.preconditions

        # Generate a LTL specification governing BDI control modes
        #FIX: infer control modes of interest from input arguments and actions
        modes_of_interest = ['stand_prep', 'stand', 'manipulate']
        ts_spec = TransitionSystemSpecification(
                                    ts = control_mode_ts,
                                    props_of_interest = modes_of_interest,
                                    outcomes = action_outcomes)

        # Generate LTL specification governing action and preconditions
        action_spec = ActionSpecification(preconditions = atlas_preconditions)
        for goal in goals:
            if goal not in ts_spec.ts.keys(): # topology is handled above
                action_spec.handle_new_action(action = goal,
                                              act_out = True,
                                              outcomes = action_outcomes)

        # Generate LTL specification governing the achievement of goals ...
        goal_spec = GoalSpecification()
        goal_spec.handle_single_liveness(goals = goals,
                                         outcomes = sm_outcomes,
                                         strict_order = strict_order)
        
        if SM_OUTCOME_FAILURE in sm_outcomes:
            # Add LTL formula tying all the things that can fail to SM outcome
            failure_conditions = ts_spec.ts.keys() + action_spec.all_actions
            assert len(failure_conditions) == len(set(failure_conditions))
            goal_spec.handle_any_failure(conditions = failure_conditions,
                                         failure = SM_OUTCOME_FAILURE)

        # Merge these specifications. Initial conditions are still missing.
        self.merge_gr1_specifications([ts_spec, action_spec, goal_spec])

        # Now generate LTL formulas encoding all of the initial conditions
        ic_spec = InitialConditionsSpecification()
        ic_spec.set_ics_from_spec(spec = self,
                                  true_props = initial_conditions)

        # Finally, also merge the initial conditions specification
        self.merge_gr1_specifications([ic_spec])


    def _check_input_arguments(self, initial_conditions, goals,
                               action_outcomes, sm_outcomes):
        
        if len(action_outcomes) > len(sm_outcomes):
            raise NotImplementedError('The specification cannot handle ' \
                                      'more action outcomes {0} ' \
                                      'than State Machine outcomes {1}'
                                      .format(action_outcomes, sm_outcomes))

# =========================================================
# Entry point
# =========================================================

def main(): #pragma: no cover
    
    import pprint
    
    specification = CompleteSpecification('atlas_example', ['stand'], ['grasp'])
    
    print "[INPUT]"
    pprint.pprint(specification.env_props)
    print "[OUTPUT]"
    pprint.pprint(specification.sys_props)
    print "[SYS_INIT]"
    pprint.pprint(specification.sys_init)
    print "[ENV_INIT]"
    pprint.pprint(specification.env_init)
    print "[SYS_TRANS]"
    pprint.pprint(specification.sys_trans)
    print "[ENV_TRANS]"
    pprint.pprint(specification.env_trans)
    print "[SYS_LIVENESS]"
    pprint.pprint(specification.sys_liveness)
    print "[ENV_LIVENESS]"
    pprint.pprint(specification.env_liveness)

if __name__ == "__main__": #pragma: no cover
    main()
