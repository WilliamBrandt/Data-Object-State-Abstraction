class GenericObject:
    def __init__(self, **attributes):
        self.__dict__.update(attributes)
    
    def exists(self):
        return True  # Implement existence check logic based on actual use case

    def state(self):
        return self.__dict__.get('state', None)  # Assuming 'state' is a common attribute

    def has_event(self, event_name):
        history = self.__dict__.get('history', [])
        return event_name in history
    
    def __str__(self):
        return str(self.__dict__)

from enum import Enum
import xml.etree.ElementTree as ET

file_path = 'processModel/orderStateDMN.dmn'

with open(file_path, 'r') as file:
    content = file.read()

# Parse the XML content
tree = ET.ElementTree(ET.fromstring(content))
root = tree.getroot()

# Namespaces are required to correctly parse the elements due to default namespaces used in the XML
namespaces = {
    'dmn': 'https://www.omg.org/spec/DMN/20191111/MODEL/'
}

# Extracting inputs, outputs, and rules
inputs = []
outputs = []
rules = []

for decision in root.findall('.//dmn:decision', namespaces):
    for decision_table in decision.findall('.//dmn:decisionTable', namespaces):
        
        # Table Name
        table_label = decision.get('name')
        if table_label:
            table_name = table_label

        # Inputs
        for input_entry in decision_table.findall('.//dmn:input', namespaces):
            input_label = input_entry.get('label')
            if input_label:
                inputs.append(input_label)

        # Outputs
        for output_entry in decision_table.findall('.//dmn:output', namespaces):
            output_label = output_entry.get('label')
            if output_label:
                outputs.append(output_label)

        # Rules
        for rule in decision_table.findall('.//dmn:rule', namespaces):
            input_entries = [ie.text for ie in rule.findall('.//dmn:inputEntry/dmn:text', namespaces)]
            output_entries = [oe.text for oe in rule.findall('.//dmn:outputEntry/dmn:text', namespaces)]
            rule_map = {'inputs': input_entries, 'outputs': output_entries}
            rules.append(rule_map)

# print('Inputs:', inputs)
# print('Outputs:', outputs)
# print('Rules:')
# for rule in rules:
#     print(rule)

class FieldType(Enum):
    state = "state"
    attribute = "attribute"
    relation = "relation"
    history = "history"


def determineType(field):
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
        raise ValueError("Field not recognized")
    
def extractOperatorAndValue(condition):
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

def refineFunction(functionType, function, object):
    # Split the function name and the argument part
    type = functionType.value
    func_name, args = function.split("(")
    args = args[:-1]  # Remove the closing parenthesis
    
    if args:
        # If there are existing arguments, add value as the first argument
        new_func_str = f"{type}_{func_name}(\"{object}\", {args})"
    else:
        # If there are no existing arguments, just add the value
        new_func_str = f"{type}_{func_name}(\"{object}\")"
    return new_func_str
    
    
def getObject(ID):
    for obj in objects:
        # compare the id of the object with the given ID
        if obj.id == ID:
            return obj        
    return None
    
def attribute_notNull(value):
    return value is not None

def attribute_exists(value):
    return value is not None

def relation_inState(value, state):
    object = getObject(value)
    if object is None:
        return False
    return object.state == state

def relation_exists(value):
    return value is not None

def history_exists(value, event):
    return event in value

# Creating an instance
invoiceId = "asda-21231-a21as"

order = GenericObject( id="123", totalamount="150", confirmed="False", history=['Create Invoice', "ArchiveOrder"], invoice=invoiceId)
invoice = GenericObject (id = invoiceId, state="paid")

objects = [order, invoice]

availableStates = []
for rule in rules:
    for output in rule['outputs']:
        availableStates.append(output)

object = order
currentStates = []
for j, rule in enumerate(rules):
    ruleFulfilled = True
    for i, condition in enumerate(rule['inputs']):
        # skip empty conditions
        if (condition is None):
            continue
        
        type, field = determineType(inputs[i])
        # skip state conditions, evaluation is done at the end
        if (field == "state"):
            continue
        
        function, operator, value = extractOperatorAndValue(condition)
        
        objectValue = getattr(object, field)
        
        if (function is not None):
            function = refineFunction(type, function, objectValue)
            ruleFulfilled = ruleFulfilled and eval(function)
        elif (operator is not None and value is not None):
            ruleFulfilled = ruleFulfilled and eval(objectValue + operator + value)
        else:
            raise ValueError(f"Invalid condition format. Condition: {condition}")
        
    # set the state
    if (ruleFulfilled):
        currentStates.append(rules[j]['outputs'][0])


def replaceStatesWithBoolean(stateCondition, availableStates, currentStates):
    missingStates = list(set(availableStates) - set(currentStates))
    for state in missingStates:
        stateCondition = stateCondition.replace(state, "False")
    for state in currentStates:
        stateCondition = stateCondition.replace(state, "True")
    return stateCondition

trueStates = []
# evaluate special state conditions
if ("state" in inputs):
    for j, rule in enumerate(rules):
        state = rule['outputs'][0]
        # only evaluate fullfilled rules
        if (state in currentStates):
            stateCondition = rule['inputs'][inputs.index("state")]
            if (stateCondition is not None):
                stateCondition = replaceStatesWithBoolean(stateCondition, availableStates, currentStates)
                if (eval(stateCondition)):
                    trueStates.append(state)
            else:
                trueStates.append(state)
                
    
print(trueStates)
