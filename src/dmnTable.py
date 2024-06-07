from typing import List
from dmnInputType import DMNInputType

class DMNInput:
    def __init__(self, label :str, type : DMNInputType):
        self.label = label
        self.type = type
        
    def __str__(self):
        return f"Input: {self.type} - {self.label}"


class DMNTable:
    # only one input of type state is allowed
    def _checkIntegrityOfInputs(self):
        if len([input for input in self.inputs if input.type == DMNInputType.state]) > 1:
            raise ValueError("Only one input of type state is allowed")
    
    def __init__(self, tablename:str, inputs : List[DMNInput]):
        self.tablename = tablename
        # only one input of type state is allowed
        self.inputs= inputs
        # the order of the states corresponds to the order of the rules!
        self.rules = []
        self.states = []
        
        self._checkIntegrityOfInputs()
        
        
    def add_rule(self, rule):
        self.rules.append(rule)

    def add_state(self, state):
        if state not in self.states:
            self.states.append(state)
            
    def getIntexOfStateInput(self):
        for i, input in enumerate(self.inputs):
            if input.type == DMNInputType.state:
                return i
        return None
        
    def hasStateInput(self):
        return any([input.type == DMNInputType.state for input in self.inputs])
            
    def __str__(self):
        str_inputs = "\n".join([f"{i}: {input}" for i, input in enumerate(self.inputs)])
        str_rules = "\n".join([f"{i}: {rule}" for i, rule in enumerate(self.rules)])
        
        return f"DMN-Table: {self.tablename}\nInputs:\n{str_inputs}\nStates: {self.states}\nRules:\n{str_rules}"