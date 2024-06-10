from dmnTable import DMNTable   
from dmnInputType import DMNInputType 


class DMNObjectFunctions():
    # depracted! not necessary
    # question is this class necessary at all?
    def notNull(self, value):
        return value is not None
    
class DMNHistoryFunctions():
    def exists(self, value, event):
        return event in value    

class DMNRelationFunctions():
    def __init__(self, evaluator, objects):
        self.evaluator = evaluator
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
        
        states = self.evaluator.evaluate(object)
        return state in states

    def exists(self, value):
        return value is not None

    
class DMNEvaluator:
    """
    DMNEvaluator is a class that evaluates an object against the rules and states defined in a DMNTable.

    The DMNEvaluator processes the object according to the rules specified in the DMNTable and returns a list of valid states for the object. It evaluates objects based on their attributes and history, utilizing the DMNTable for the evaluation process.
    
    Args:
    dmn_tables (list of DMNTable): List of DMNTables that have a DMNTable for each class
    objects (list, optional): Defaults to []. List of objects that are used in the evaluation
    debugging (bool, optional): Defaults to False. If set to true, the evaluator prints debug information

    Returns:
    list: List of states that are fulfilled
    
    Raises:
    ValueError: If the condition format is invalid
    """
    
    
    def __init__(self, dmn_tables : list[DMNTable], objects = [], debugging = False):
        """
        Args:
            dmn_tables (list of DMNTable): List of DMNTables that have a DMNTable for each class
            objects (list, optional): Defaults to []. List of objects that are used in the evaluation
            debugging (bool, optional): Defaults to False. If set to true, the evaluator prints debug information
        """
        
        self.debugging = debugging
        self.dmnTables = dmn_tables
        self.functions_history = DMNHistoryFunctions()
        self.functions_relation = DMNRelationFunctions(self, objects)
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
            new_func_str = f"self.functions_{type}.{func_name}({object}, {args})"
        else:
            # If there are no existing arguments, just add the value
            new_func_str = f"self.functions_{type}.{func_name}({object})"
        return new_func_str
    
    def _refineValue(self, value):
        if value is None:
            return "None"
        elif isinstance (value, list):
            return value
        elif value == "True" or value == "False":
            return value
        elif isinstance (value, (int, float)):
            return value
        else:
            return f'"{value}"' 

    def _replaceStatesWithBoolean(self, stateCondition, availableStates, currentStates):
        missingStates = list(set(availableStates) - set(currentStates))
        for state in missingStates:
            stateCondition = stateCondition.replace(state, "False")
        for state in currentStates:
            stateCondition = stateCondition.replace(state, "True")
        return stateCondition
    
    
    def getDMNTable(self, object):
        for dmnTable in self.dmnTables:
            if dmnTable.tablename == object.clazz:
                return dmnTable
        return None

    def evaluate(self, object):
        
        dmnTable = self.getDMNTable(object)
        if (dmnTable is None):
            raise ValueError(f"No DMNTable found for class: {object.clazz}\nPossible classes: {[table.tablename for table in self.dmnTables]}")
        
        
        possibleStates = []
        for j, rule in enumerate(dmnTable.rules):
            ruleFulfilled = True
            for i, condition in enumerate(rule):
                if (condition is None) or (condition == ""):
                    continue
                input =  dmnTable.inputs[i]
                if input.type == DMNInputType.state:
                    continue
                function, operator, value = self._extractOperatorAndValue(condition)
                objectValue = getattr(object, input.label)
                objectValue = self._refineValue(objectValue)
                if function is not None:
                    function = self._refineFunction(input.type, function, objectValue)
                    if (self.debugging):
                        print(f"Executing function: {function}")
                    ruleFulfilled = ruleFulfilled and eval(function)
                elif operator is not None and value is not None:
                    if (self.debugging):
                        print(f"Evaluating term: {objectValue} {operator} {value}")
                    ruleFulfilled = ruleFulfilled and eval(str(objectValue) + str(operator) + str(value))
                else:
                    raise ValueError(f"Invalid condition format. Condition: {condition}")
            if (self.debugging):
                print(f"Rule {j} evaluated to: {ruleFulfilled}")
            if ruleFulfilled:
                possibleStates.append(dmnTable.states[j])
                
        validStates = []
        if dmnTable.hasStateInput():
            for j, rule in enumerate(dmnTable.rules):
                state = dmnTable.states[j]
                if state in possibleStates:
                    stateCondition = rule[dmnTable.getIntexOfStateInput()]
                    if stateCondition is not None:
                        stateCondition = self._replaceStatesWithBoolean(stateCondition, dmnTable.states, possibleStates)
                        if eval(stateCondition):
                            validStates.append(state)
                    else:
                        validStates.append(state)
        else:
            validStates = possibleStates
        if (self.debugging):
            print(f"Object: {object.id} from class: {object.clazz} has states:{validStates}")
        return validStates