from dmnTable import DMNTable   
from dmnInputType import DMNInputType 

class DMNObjectFunctions():
    def notNull(self, value):
        return value is not None

    def exists(self, value):
        return value is not None
    
class DMNHistoryFunctions():
    def exists(self, value, event):
        return event in value    

class DMNRelationFunctions():
    def __init__(self, objects):
        self.objects = objects
    
    def _getObject(self, ID):
        for obj in self.objects:
            if obj.id == ID:
                return obj
        return None
    
    def inState(self, value, state):
        object = self._getObject(value)
        if object is None:
            return False
        return object.state == state

    def exists(self, value):
        return value is not None

    
class DMNEvaluator:
    def __init__(self, dmn_table : DMNTable, objects):
        self.dmnTable = dmn_table
        self.functions_history = DMNHistoryFunctions()
        self.functions_relation = DMNRelationFunctions(objects)
        self.functions_object = DMNObjectFunctions()
        
    
    def _extractOperatorAndValue(self, condition):
        value = None
        operator = None
        function = None
        conditionSize = len(condition.split())
        if (conditionSize == 1):
            # two possibilities: either a function or a value
            
            # check if it is a function
            if (condition.endswith(")")):
                function = condition
            else:
                operator = "=="
                value = condition
        elif (conditionSize == 2):
            operator = condition.split()[0]
            value = condition.split()[1]
        else:
            raise ValueError(f"Invalid condition format. Condition: {condition}")
        return function, operator, value
        
    def _refineFunction(self, functionType, function, object):
        # Split the function name and the argument part
        type = functionType.value
        func_name, args = function.split("(")
        args = args[:-1]  # Remove the closing parenthesis
        
        if args:
            # If there are existing arguments, add value as the first argument
            new_func_str = f"self.functions_{type}.{func_name}(\"{object}\", {args})"
        else:
            # If there are no existing arguments, just add the value
            new_func_str = f"self.functions_{type}.{func_name}(\"{object}\")"
        return new_func_str

    def _replaceStatesWithBoolean(self, stateCondition, availableStates, currentStates):
        missingStates = list(set(availableStates) - set(currentStates))
        for state in missingStates:
            stateCondition = stateCondition.replace(state, "False")
        for state in currentStates:
            stateCondition = stateCondition.replace(state, "True")
        return stateCondition

    def evaluate(self, object):
        currentStates = []
        for j, rule in enumerate(self.dmnTable.rules):
            ruleFulfilled = True
            for i, condition in enumerate(rule):
                if condition is None:
                    continue
                input = self.dmnTable.inputs[i]
                if input.type == DMNInputType.state:
                    continue
                function, operator, value = self._extractOperatorAndValue(condition)
                objectValue = getattr(object, input.label)
                if function is not None:
                    function = self._refineFunction(input.type, function, objectValue)
                    ruleFulfilled = ruleFulfilled and eval(function)
                elif operator is not None and value is not None:
                    ruleFulfilled = ruleFulfilled and eval(objectValue + operator + value)
                else:
                    raise ValueError(f"Invalid condition format. Condition: {condition}")
            if ruleFulfilled:
                currentStates.append(self.dmnTable.states[j])
                
        trueStates = []
        if self.dmnTable.hasStateInput():
            for j, rule in enumerate(self.dmnTable.rules):
                state = self.dmnTable.states[j]
                if state in currentStates:
                    stateCondition = rule[self.dmnTable.getIntexOfStateInput()]
                    if stateCondition is not None:
                        stateCondition = self._replaceStatesWithBoolean(stateCondition, self.dmnTable.states, currentStates)
                        if eval(stateCondition):
                            trueStates.append(state)
                    else:
                        trueStates.append(state)
        else:
            trueStates = currentStates
        return trueStates