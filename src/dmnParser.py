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

# Parsing code
dmn_tables = []


for decision in root.findall('.//dmn:decision', namespaces):
    for decision_table in decision.findall('.//dmn:decisionTable', namespaces):
        
        # Table Name
        table_label = decision.get('name')
        if table_label:
            table_name = table_label


        inputs = []
        # Inputs
        for input_entry in decision_table.findall('.//dmn:input', namespaces):
            input_label = input_entry.get('label')
            if input_label:
                inputs.append(input_label)

        # Create DMNTable instance
        dmn_table = DMNTable(table_name, inputs)

        # Rules
        for rule in decision_table.findall('.//dmn:rule', namespaces):
            input_entries = [ie.text for ie in rule.findall('.//dmn:inputEntry/dmn:text', namespaces)]
            output_entries = [oe.text for oe in rule.findall('.//dmn:outputEntry/dmn:text', namespaces)]
            dmn_table.add_rule(input_entries)
            if (len(output_entries) == 0 or len(output_entries) > 1):
                raise ValueError(f"Invalid number of output entries. Expected 1, got {len(output_entries)}")
            dmn_table.add_state(output_entries[0])
        dmn_tables.append(dmn_table)

print(dmn_tables[0])

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

table = dmn_tables[0]
objects = [order, invoice]

object = order
currentStates = []
for j, rule in enumerate(table.rules):
    ruleFulfilled = True
    for i, condition in enumerate(rule):
        # skip empty conditions
        if (condition is None):
            continue
        
        type, field = determineType(table.inputs[i])
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
        currentStates.append(table.states[j])


def replaceStatesWithBoolean(stateCondition, availableStates, currentStates):
    missingStates = list(set(availableStates) - set(currentStates))
    for state in missingStates:
        stateCondition = stateCondition.replace(state, "False")
    for state in currentStates:
        stateCondition = stateCondition.replace(state, "True")
    return stateCondition

trueStates = []
# evaluate special state conditions
if ("state" in table.inputs):
    for j, rule in enumerate(table.rules):
        state = table.states[j]
        # only evaluate fullfilled rules
        if (state in currentStates):
            stateCondition = rule[table.inputs.index("state")]
            if (stateCondition is not None):
                stateCondition = replaceStatesWithBoolean(stateCondition, table.states, currentStates)
                if (eval(stateCondition)):
                    trueStates.append(state)
            else:
                trueStates.append(state)
                
    
print(trueStates)
