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
# sometimes the OCEL json validation fails nevertheless the json is correct, in this case set validate_json=False
ocel.parse_and_store(ocelPath, validate_json=True)
objects = ocel.get_objects_with_events_and_foreign_key()

# Initialize evaluator and test for cyclic state dependencies
evaluator = DMNEvaluator(dmnTables, objects, debugging=True)

# Method to display data object state dependencies
evaluator.visualizeGraph()

# Evaluate the first order object
order = objects[0]
validStates = evaluator.evaluate(order)


# To work with the order-management OCEL officially provided on the OCEL 2.0 website, download the
# order-management.json file from the following link: https://doi.org/10.5281/zenodo.8337463
# and place it in the data directory. Then, uncomment the following lines and comment the previous ones.
# orderDMNpath = '../data/order-management.dmn'
# ocelPath = '../data/order-management.json'

# parser = DMNParser()
# orderDMN = parser.parse(orderDMNpath)
# dmnTables = [orderDMN[0]] # '[0]' is necessary because the parser returns a list of DMNTables

# ocel = OCEL()
# ocel.parse_and_store(ocelPath, validate_json=False)
# objects = ocel.get_objects_with_events_and_foreign_key()

# evaluator = DMNEvaluator(dmnTables, objects, debugging=False)

# numOrders = 0
# stateOccurrences = {}

# for obj in objects:
#   if obj.clazz == 'orders':
#     numOrders += 1
#     states = evaluator.evaluate(obj)
#     tuples = tuple(states)
    
#     # Count the number of occurrences of each state combination
#     if tuples in stateOccurrences:
#         stateOccurrences[tuples] += 1
#     else:
#         stateOccurrences[tuples] = 1
    
# print("From the " + str(numOrders) + " orders. The following state combinations occured:")
# print(stateOccurrences)
