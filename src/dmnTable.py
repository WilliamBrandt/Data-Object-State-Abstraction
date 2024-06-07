class DMNTable:
    def __init__(self, tablename, inputs):
        self.tablename = tablename
        self.inputs = inputs
        # the order of the states corresponds to the order of the rules!
        self.rules = []
        self.states = []
        
    def add_rule(self, rule):
        self.rules.append(rule)

    def add_state(self, state):
        if state not in self.states:
            self.states.append(state)
            
    def __str__(self):
        str_rules = "\n".join([f"{i}: {rule}" for i, rule in enumerate(self.rules)])
        
        return f"DMN-Table: {self.tablename}\nStates: {self.states}\nRules:\n{str_rules}"