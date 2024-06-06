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





class EmptyExpression:
    def evaluate(self, obj):
        return True

class Expression(EmptyExpression):
    def __init__(self, attribute):
        self.attribute = attribute
    
    def evaluate(self, obj):
        raise NotImplementedError("Evaluate method must be implemented in derived classes")

    def evaluate(self, operator, object):
        if (operator == ''):
            return object == self.attribute
        if (operator == "notNull()"):
            return object is not None
        if (operator == ">"):
            return object > self.attribute
        if (operator == "<"):
            return object < self.attribute

class EqualityExpression(Expression):
    def evaluate(self, obj):
        return obj == self.attribute

class GreaterThanExpression(Expression):
    def evaluate(self, obj):
        return obj > self.attribute

class LessThanExpression(Expression):
    def evaluate(self, obj):
        return obj < self.attribute
    
class NotNullExpression(EmptyExpression):
    def evaluate(self, obj):
        print(obj)
        return obj is not None

class Rule:
    def __init__(self, source, condition):
        self.source = source
        self.condition = condition
        self.type = 'generic'
    
    def evaluate(self, obj):
        return self.condition(obj)

class RelationRule(Rule):
    def evaluate(self, obj):
        return super().evaluate(obj)

class AttributeRule(Rule):
    def __init__(self, source, condition):
        super().__init__(source, condition)
        self.type = 'attribute'
        
    def evaluate(self, obj):
        value = getattr(obj, self.source)
        return super().evaluate(value)





class ExpressionEvaluator:
    
    def __init__(self, inputs, outputs, rules):
        self.inputs = inputs
        self.outputs = outputs
        self.rules = rules

    def parse_expression(self):
        # Naive parser for operations: assumes simple format "attr1.attr2... op value"
        parts = self.expression.split()
        if len(parts) == 3:
            attribute, operation, value = parts
            value = float(value)  # Convert value to a number (float)
        else:
            attribute = self.expression
            operation = None
            value = None
        return attribute, operation, value

    def evaluate(self, obj):
        attribute, operation, value = self.parse_expression()
        # Navigate through attributes
        for attr in attribute.split('.'):
            obj = getattr(obj, attr, None)
            if obj is None:
                raise ValueError(f"Attribute {attr} not found")
        
        # Apply operation
        if operation and value is not None:
            if operation == '+':
                return obj + value
            elif operation == '-':
                return obj - value
            elif operation == '*':
                return obj * value
            elif operation == '/':
                return obj / value
        return obj



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


# print the extracted data
# in readalbe format
# each rule is a dictionary with keys 'condition' and 'outputs'

print('Inputs:', inputs)
print('Outputs:', outputs)
print('Rules:')
for rule in rules:
    print(rule)

# Creating an instance
order = GenericObject(state="None", D=123, total_amount=150, confirmed=True, history=['Event1'])

print(order)

eqExp = EqualityExpression('valid')
notNull = NotNullExpression()
rule = AttributeRule('state', notNull.evaluate)
print(rule.evaluate(order))


# print(order)

# Evaluating rules
# states = evaluate_dmn_rules(order, rules)
