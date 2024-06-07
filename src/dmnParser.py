from dmnTable import DMNTable
import xml.etree.ElementTree as ET

class DMNParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.namespaces = {
            'dmn': 'https://www.omg.org/spec/DMN/20191111/MODEL/'
        }
        self.decision_string = './/dmn:decision'
        self.decision_table_string = './/dmn:decisionTable'
        self.input_string = './/dmn:input'
        self.rule_string = './/dmn:rule'
        self.input_entry_string = './/dmn:inputEntry/dmn:text'
        self.output_entry_string = './/dmn:outputEntry/dmn:text'

    def parse(self):
        with open(self.file_path, 'r') as file:
            content = file.read()

        # Parse the XML content
        tree = ET.ElementTree(ET.fromstring(content))
        root = tree.getroot()

        # Parsing code
        dmn_tables = []

        for decision in root.findall(self.decision_string, self.namespaces):
            for decision_table in decision.findall(self.decision_table_string, self.namespaces):
                
                # Table Name
                table_label = decision.get('name')
                if table_label:
                    table_name = table_label

                inputs = []
                # Inputs
                for input_entry in decision_table.findall(self.input_string, self.namespaces):
                    input_label = input_entry.get('label')
                    if input_label:
                        inputs.append(input_label)

                # Create DMNTable instance
                dmn_table = DMNTable(table_name, inputs)

                # Rules
                for rule in decision_table.findall(self.rule_string, self.namespaces):
                    input_entries = [ie.text for ie in rule.findall(self.input_entry_string, self.namespaces)]
                    output_entries = [oe.text for oe in rule.findall(self.output_entry_string, self.namespaces)]
                    dmn_table.add_rule(input_entries)
                    if (len(output_entries) == 0 or len(output_entries) > 1):
                        raise ValueError(f"Invalid number of output entries. Expected 1, got {len(output_entries)}")
                    dmn_table.add_state(output_entries[0])
                dmn_tables.append(dmn_table)

        return dmn_tables