from dmnParser import DMNParser
from dmnEvaluator import DMNEvaluator
from genericObject import GenericObject


orderDMNpath = 'processModel/orderStateDMN.dmn'
invoiceDMNpath = 'processModel/invoiceStateDMN.dmn'

parser = DMNParser()
orderDMN = parser.parse(orderDMNpath)
invoiceDMN = parser.parse(invoiceDMNpath)

# '[0]' is necessary because the parser returns a list of DMNTables
dmnTables = [orderDMN[0], invoiceDMN[0]]

# Creating an instance
invoiceId = "asda-21231-a21as"
order = GenericObject(clazz="class.order", id="123", totalamount=150, confirmed=True, history=['Create Invoice', "ArchiveOrder"], invoice=invoiceId)
invoice = GenericObject (clazz="class.invoice", id = invoiceId, receivedate="2024-05-30", history=["SentInvoice"])

objects = [order, invoice]
object = order

evaluator = DMNEvaluator(dmnTables, objects, debugging=True)
validStates = evaluator.evaluate(object)

print(validStates)
