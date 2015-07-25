#!/usr/bin/env python

from gr1_specification import GR1Specification
from ..formula import *

"""
Module's docstring #TODO
"""

class InitialConditionsSpecification(GR1Specification):
    """
    docstring for InitialConditionsSpecification
    """
    def __init__(self, name = ''):
        super(InitialConditionsSpecification, self).__init__(spec_name = name,
                                                             env_props = [],
                                                             sys_props = [])

    def set_ics_from_spec(self, spec, true_props):
        """
        Use the propositions of another specification to generate system 
        and environment initial condition formulas for this specification.
        """

        #Activation props should all be False in new IC paradigm:
        self.sys_init = SystemInitialConditions(spec.sys_props,
                                                true_props = []).formulas
        
        self.env_init = EnvironmentInitialConditions(spec.env_props,
                                                     true_props).formulas
