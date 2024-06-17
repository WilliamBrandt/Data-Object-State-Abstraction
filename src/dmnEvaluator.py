from dmnTable import DMNTable, DMNInput
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
        
    
    
    def _refineValue(self, value):
        if value is None:
            return "None"
        elif isinstance (value, list):
            return value
        elif value == "True" or value == "False":
            return value
        else:
            try:
                number = int(value)
                return number
            except:
                return f'"{value}"'                
    
    def _getObjectValue(self, object, attribute : DMNInput):
        objectValue = getattr(object, attribute.label)
        return self._refineValue(objectValue)
    
    def _isFunction(self, term):
        return term.endswith(")")
    
    def _isOperator(self, term):
        return term in ["==", "!=", ">", "<", ">=", "<="]
    
    def _isConjunction(self, term):
        return term in ["and", "or"]
    
    def _isValue(self, term):
        return (term is not None) and (term != "") and (not(self._isFunction(term))) and (not(self._isOperator(term))) and (not(self._isConjunction(term)))
    
    # given a function, return the inner function
    # e.g. "not(exists())" -> "not, exists()"
    def _splitFunctionInInnerAndOuter(self, function):
        start = function.find("(")
        end = function.rfind(")")
        return function[:start],function[start+1:end]
    
    def smart_split(self, expression):
        all_fragments = expression.split()
        if (len(all_fragments) == 1):
            return all_fragments
        
        fragments = []
        
        innerFunction = False
        functionLevel = 0
        for i, term in enumerate(all_fragments):
            if "(" in term:
                start = i
                functionLevel += 1
                innerFunction = True
            if ")" in term:
                end = i
                functionLevel -= 1
            if functionLevel == 0:
                if innerFunction:
                    fragments.append(" ".join(all_fragments[start:end+1]))
                    innerFunction = False
                else:
                    fragments.append(term)
        return fragments
    
    def _getExpression(self, object, input : DMNInput, condition : str):
        fragment = condition.split()
        fragment = self.smart_split(condition)
        return self._evaluateExpression(object, input, None, fragment[0], fragment[1:])       
    
    def _evaluateExpression(self, object, input : DMNInput,prefix, term, fragment = []):
        expression = ""
        # add spacing if there is a prefix:
        if (prefix is not None):
            expression += " "
            
        if self._isFunction(term):
            outerTerm, innerTerm = self._splitFunctionInInnerAndOuter(term)
            innerTerm = self._evaluateInnerFunctionTerm(object, input, innerTerm)
            outerTerm = self._evaluateOuterFunctionTerm(input, outerTerm)
            expression += f"{outerTerm}({innerTerm})"
            
        elif self._isOperator(term):
            if (not(self._isValue(prefix))):
                expression += f"{self._getObjectValue(object, input)} "
            expression += f"{term}"
            
        elif self._isConjunction(term):
            expression += f"{term}"
            
        elif self._isValue(term):
            if (prefix is None):
                expression += f"{self._getObjectValue(object, input)} == "
            expression += f"{term}"
            
        else:
            raise ValueError(f"Invalid term: {term}")
        
        if (len(fragment) > 0):
            expression += self._evaluateExpression(object, input, term, fragment[0], fragment[1:])
        return expression

    def _evaluateRelationFunctionTerm(self, object, input : DMNInput, innerTerm):
        relatedObjects = str(object.related_objects[input.label])
        if innerTerm == "" or innerTerm is None:
            return relatedObjects
        return relatedObjects + "," + innerTerm
    def _evaluateInnerFunctionTerm(self, object, input, innerTerm):
        if input.type == DMNInputType.relation:
            innerTerm = self._evaluateRelationFunctionTerm(object, input, innerTerm)
        elif (innerTerm == "" or innerTerm is None):
            innerTerm = self._getObjectValue(object, input)
        else:
            fragment = self.smart_split(innerTerm)
            if (len(fragment) == 1 and self._isValue(innerTerm)):
                innerTerm = str(self._getObjectValue(object, input)) + "," + innerTerm
            else:
                if (len(fragment) == 1):
                    innerTerm = self._evaluateExpression(object, input, None, fragment[0],[])
                else:
                    innerTerm = self._evaluateExpression(object, input, None, fragment[0], fragment[1:] )
        return innerTerm
        
    def _evaluateOuterFunctionTerm(self,input : DMNInput, function):
        buildInFunctions = ["not"]
        if function in buildInFunctions:
            return function
        
        type = input.type.value
        return f"self.functions_{type}.{function}"
        
    


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
                expression = self._getExpression(object, input, condition)
                if (self.debugging):
                    print(f"Expression: {expression}")
                ruleFulfilled = ruleFulfilled and eval(expression)
                
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