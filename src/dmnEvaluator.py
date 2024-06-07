from enum import Enum

class FieldType(Enum):
    state = "state"
    attribute = "attribute"
    relation = "relation"
    history = "history"
                
                
class DMNFunctions():
    def __init__(self, objects):
        self.objects = objects
    
    def getObject(self, ID):
        for obj in self.objects:
            if obj.id == ID:
                return obj
        return None

    def attribute_notNull(self, value):
        return value is not None

    def attribute_exists(self, value):
        return value is not None

    def relation_inState(self, value, state):
        object = self.getObject(value)
        if object is None:
            return False
        return object.state == state

    def relation_exists(self, value):
        return value is not None

    def history_exists(self, value, event):
        return event in value    
                
    
class DMNEvaluator:
    def __init__(self, dmn_table, objects):
        self.dmn_table = dmn_table
        self.functions = DMNFunctions(objects)
    
    def _determineType(self, field):
        field = field.lower()
        if field == "state":
            return FieldType.state, field
        elif field.startswith("object."):
            return FieldType.attribute, field.replace("object.", "")
        elif field.startswith("relation."):
            return FieldType.relation, field.replace("relation.", "")
        elif field == "history":
            return FieldType.history, field
        else:
            raise ValueError(f"Field not recognized. Field: {field}")
    
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
            new_func_str = f"self.functions.{type}_{func_name}(\"{object}\", {args})"
        else:
            # If there are no existing arguments, just add the value
            new_func_str = f"self.functions.{type}_{func_name}(\"{object}\")"
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
        for j, rule in enumerate(self.dmn_table.rules):
            ruleFulfilled = True
            for i, condition in enumerate(rule):
                if condition is None:
                    continue
                type, field = self._determineType(self.dmn_table.inputs[i])
                if field == "state":
                    continue
                function, operator, value = self._extractOperatorAndValue(condition)
                objectValue = getattr(object, field)
                if function is not None:
                    function = self._refineFunction(type, function, objectValue)
                    print(function)
                    ruleFulfilled = ruleFulfilled and eval(function)
                elif operator is not None and value is not None:
                    ruleFulfilled = ruleFulfilled and eval(objectValue + operator + value)
                else:
                    raise ValueError(f"Invalid condition format. Condition: {condition}")
            if ruleFulfilled:
                currentStates.append(self.dmn_table.states[j])

        trueStates = []
        if "state" in self.dmn_table.inputs:
            for j, rule in enumerate(self.dmn_table.rules):
                state = self.dmn_table.states[j]
                if state in currentStates:
                    stateCondition = rule[self.dmn_table.inputs.index("state")]
                    if stateCondition is not None:
                        stateCondition = self._replaceStatesWithBoolean(stateCondition, self.dmn_table.states, currentStates)
                        if eval(stateCondition):
                            trueStates.append(state)
                    else:
                        trueStates.append(state)
        return trueStates