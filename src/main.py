from dmnParser import DMNParser
from dmnEvaluator import DMNEvaluator
from ocel2Parser import OCEL

# Define paths to data files
orderDMNpath = '../data/O2C_orderStateDMN.dmn'
invoiceDMNpath = '../data/O2C_invoiceStateDMN.dmn'
ocelPath = '../data/O2C_event_log.json'
# Uncomment the line below to use the OCEL file with the DeliverOrder event
# ocelPath = '../data/O2C_event_log_with_DeliverOrder.json'

# Parse DMN tables
parser = DMNParser()
orderDMN = parser.parse(orderDMNpath)
invoiceDMN = parser.parse(invoiceDMNpath)
dmnTables = [orderDMN[0], invoiceDMN[0]] # '[0]' is necessary because the parser returns a list of DMNTables

# Extract objects from OCEL
ocel = OCEL()
ocel.parse_and_store(ocelPath)
objects = ocel.get_objects_with_events_and_foreign_key()

# Initialize evaluator and test for cyclic state dependencies
evaluator = DMNEvaluator(dmnTables, objects, debugging=True)

# Method to display data object state dependencies
#evaluator.visualizeGraph()

# Evaluate the order object
order = objects[0]
validStates = evaluator.evaluate(order)
