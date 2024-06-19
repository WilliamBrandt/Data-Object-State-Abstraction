from dmnParser import DMNParser
from dmnEvaluator import DMNEvaluator
from genericObject import GenericObject
from ocel2Parser import OCEL
import pathlib

# Define paths to data files
path = str(pathlib.Path().resolve())
orderDMNpath = path + '/data/orderStateDMN.dmn'
invoiceDMNpath = path + '/data/invoiceStateDMN.dmn'
ocelPath = path + '/data/ocelExample.json'

# Parse DMN tables
parser = DMNParser()
orderDMN = parser.parse(orderDMNpath)
invoiceDMN = parser.parse(invoiceDMNpath)

dmnTables = [orderDMN[0], invoiceDMN[0]] # '[0]' is necessary because the parser returns a list of DMNTables


# Creating an instance
ocel = OCEL()
# default loads /processModel/ocelExample.json
ocel.parse_and_store(ocelPath)

# generate needed objects
objects = ocel.get_objects_with_history_and_foreign_key()
object = objects[0]
print (object)

evaluator = DMNEvaluator(dmnTables, objects, debugging=True)

# evaluator.visualizeGraph()
validStates = evaluator.evaluate(object)

print(validStates)
