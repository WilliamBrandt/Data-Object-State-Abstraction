from dmnTable import DMNTable, DMNInput
from dmnInputType import DMNInputType
from dmnGraph import DMNGraph


class DMNEventsFunctions():
    def amount(self, log, event):
        return log.count(event)


class DMNLinkFunctions():
    def __init__(self, evaluator, objects):
        self.evaluator = evaluator
        self.objects = objects

    def _getObject(self, ID):
        for obj in self.objects:
            if obj.id == ID:
                return obj
        return None

    def _getRelatedObjects(self, objectID, clazz):
        obj = self._getObject(objectID)
        if obj is None:
            return []
        if clazz not in obj.related_objects:
            return []
        relatedObjects = obj.related_objects[clazz]
        objects = []
        for relatedObject in relatedObjects:
            obj = self._getObject(relatedObject)
            if obj is not None:
                objects.append(obj)
        return objects
    def amount(self, objectID, classType, state = None):
        relatedObjects = self._getRelatedObjects(objectID, classType)

        if state is None:
            return len(relatedObjects)

        objects = []
        for relatedObject in relatedObjects:
            if state in self.evaluator.evaluate(relatedObject, "> "):
                objects.append(relatedObject)

        return len(objects)


class DMNEvaluator:
    """
    DMNEvaluator is a class that evaluates an object against the rules and states defined in a DMNTable.

    The DMNEvaluator processes the object according to the rules specified in the DMNTable and returns a list of valid states for the object. It evaluates objects based on their attributes and events, utilizing the DMNTable for the evaluation process.
    
    Args:
    dmn_tables (list of DMNTable): List of DMNTables that have a DMNTable for each class
    objects (list, optional): Defaults to []. List of objects that are used in the evaluation
    debugging (bool, optional): Defaults to False. If set to true, the evaluator prints debug information

    Returns:
    list: List of states that are fulfilled
    
    Raises:
    ValueError: If the condition format is invalid
    """

    def __init__(self, dmn_tables: list[DMNTable], objects=[], debugging=False):
        """
        Args:
            dmn_tables (list of DMNTable): List of DMNTables that have a DMNTable for each class
            objects (list, optional): Defaults to []. List of objects that are used in the evaluation
            debugging (bool, optional): Defaults to False. If set to true, the evaluator prints debug information
        """

        self.debugging = debugging
        self.dmnTables = dmn_tables
        self.functions_events = DMNEventsFunctions()
        self.functions_link = DMNLinkFunctions(self, objects)

        self.graph = DMNGraph(dmn_tables, debugging)

        if self.graph.isCyclic():
            print("Cyclic dependency in DMNTables! Cannot evaluate cyclic dependencies.")
            self.visualizeGraph()
            raise ValueError("Cyclic dependency in DMNTables! Cannot evaluate cyclic dependencies.")

    def visualizeGraph(self):
        self.graph.drawGraph()

    def _refineValue(self, value):
        if value is None or value == "" or value == "None":
            return "None"
        elif isinstance(value, list):
            return value
        elif value == "True" or value == "False":
            return value
        else:
            try:
                number = int(value)
                return number
            except:
                return f'"{value}"'

    def _getObjectValue(self, object, attribute: DMNInput):
        objectValue = getattr(object, attribute.label)
        return self._refineValue(objectValue)

    def _isFunction(self, term):
        return term.endswith(")")

    def _isOperator(self, term):
        return term in ["==", "!=", ">", "<", ">=", "<="]

    def _isConjunction(self, term):
        return term in ["and", "or"]

    def _isValue(self, term):
        return (term is not None) and (term != "") and (not (self._isFunction(term))) and (
            not (self._isOperator(term))) and (not (self._isConjunction(term)))

    # given a function, return the inner function
    # e.g. "not(exists())" -> "not, exists()"
    def _splitFunctionInInnerAndOuter(self, function):
        start = function.find("(")
        end = function.rfind(")")
        return function[:start], function[start + 1:end]


    def _split_expression_into_tokens(self, expression):
        # First, we parse the expression into tokens taking into account quoted strings.
        # We'll consider both single and double quotes as possible delimiters.
        tokens = []
        current_token = []
        in_quotes = False
        quote_char = None

        for char in expression:
            if in_quotes:
                # If we're inside quotes, we only exit if we encounter the same quote character
                if char == quote_char:
                    in_quotes = False
                current_token.append(char)
            else:
                # If we're not inside quotes, we watch for the start of quotes
                if char in ('"', "'"):
                    in_quotes = True
                    quote_char = char
                    current_token.append(char)
                elif char.isspace():
                    # Outside quotes, space indicates a token boundary
                    if current_token:
                        tokens.append("".join(current_token))
                        current_token = []
                else:
                    current_token.append(char)

        # Add the last token if present
        if current_token:
            tokens.append("".join(current_token))
        return tokens


    def smart_split(self, expression):
        all_fragments = self._split_expression_into_tokens(expression)
        if (len(all_fragments) == 1):
            return all_fragments

        fragments = []

        innerFunction = False
        functionLevel = 0
        for i, term in enumerate(all_fragments):
            if "(" in term:
                function_start_index = i
                functionLevel += 1
                innerFunction = True
            if ")" in term:
                end = i
                functionLevel -= 1
            if functionLevel == 0:
                if innerFunction:
                    fragments.append(" ".join(all_fragments[function_start_index:end + 1]))
                    innerFunction = False
                else:
                    fragments.append(term)
        return fragments

    def _getExpression(self, object, input: DMNInput, condition: str):
        fragment = condition.split()
        fragment = self.smart_split(condition)
        return self._evaluateExpression(object, input, None, fragment[0], fragment[1:])

    def _evaluateExpression(self, object, input: DMNInput, prefix, term, fragment=[]):
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
            if prefix is None or self._isConjunction(prefix):
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

    def _evaluateLinkFunctionTerm(self, object, input: DMNInput, innerTerm):
        # if input.label in object.related_objects:
        id = object.id
        clazz = input.label
        relatedObjects = f"'{id}','{clazz}'"

        # relatedObjects = self._refineValue(object.related_objects[input.label][0])
        if innerTerm == "" or innerTerm is None:
            return relatedObjects
        return relatedObjects + "," + innerTerm
        # return None

    def _evaluateInnerFunctionTerm(self, object, input, innerTerm):
        if (innerTerm == "" or innerTerm is None):
            if input.type == DMNInputType.link:
                innerTerm = self._evaluateLinkFunctionTerm(object, input, innerTerm)
            else:
                innerTerm = self._getObjectValue(object, input)
        else:
            fragment = self.smart_split(innerTerm)
            if (len(fragment) == 1 and self._isValue(innerTerm)):
                if input.type == DMNInputType.link:
                    innerTerm = self._evaluateLinkFunctionTerm(object, input, innerTerm)
                else:
                    innerTerm = str(self._getObjectValue(object, input)) + "," + innerTerm
            else:
                if (len(fragment) == 1):
                    innerTerm = self._evaluateExpression(object, input, None, fragment[0], [])
                else:
                    innerTerm = self._evaluateExpression(object, input, None, fragment[0], fragment[1:])
        return innerTerm

    def _evaluateOuterFunctionTerm(self, input: DMNInput, function):
        buildInFunctions = ["not"]
        if function in buildInFunctions:
            return function
        # cases like (> 5) or (== 5)
        if function == "":
            return ""

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

    def evaluate(self, object, debugging_prefix=""):
        if (self.debugging):
            print(f"\n{debugging_prefix}Evaluating object: {object.id} from class: {object.clazz}")
            print(f"{debugging_prefix}{object}")

        dmnTable = self.getDMNTable(object)
        if (dmnTable is None):
            raise ValueError(
                f"No DMNTable found for class: {object.clazz}\nPossible classes: {[table.tablename for table in self.dmnTables]}")

        possibleStates = []
        for j, rule in enumerate(dmnTable.rules):
            ruleFulfilled = True
            if (self.debugging):
                print(f"\n{debugging_prefix}Conditions for state: {dmnTable.states[j]}")
                print(f"{debugging_prefix}Condition {j}: {rule}")

            for i, condition in enumerate(rule):
                if (condition is None) or (condition == ""):
                    continue
                input = dmnTable.inputs[i]
                if input.type == DMNInputType.state:
                    continue
                expression = self._getExpression(object, input, condition)
                if (self.debugging):
                    print(f"{debugging_prefix}Expression: {expression}")
                ruleFulfilled = ruleFulfilled and eval(expression)

            if (self.debugging):
                print(f"{debugging_prefix}Condition evaluated to: {ruleFulfilled}")
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
        print(f"\n{debugging_prefix}Object: {object.id} from class: {object.clazz} has states:{validStates}")
        return validStates
