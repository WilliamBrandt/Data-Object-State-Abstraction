from dmnParser import DMNParser
from dmnEvaluator import DMNEvaluator
from genericObject import GenericObject


file_path = 'processModel/orderStateDMN.dmn'
parser = DMNParser(file_path)
tables = parser.parse()

# Creating an instance
invoiceId = "asda-21231-a21as"
order = GenericObject( id="123", totalamount="150", confirmed="False", history=['Create Invoice', "ArchiveOrder"], invoice=invoiceId)
invoice = GenericObject (id = invoiceId, state="paid")

table = tables[0]
objects = [order, invoice]

object = order

evaluator = DMNEvaluator(table, objects)
trueStates = evaluator.evaluate(object)

print(trueStates)
