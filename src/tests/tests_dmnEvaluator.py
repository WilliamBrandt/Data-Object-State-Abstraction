import unittest
import sys
import os

# Calculate the path to the src directory relative to this file's location
current_dir = os.path.dirname(__file__)
src_dir = os.path.join(current_dir, '..')
src_dir = os.path.abspath(src_dir)

# Add the src directory to sys.path to make the imports work
sys.path.append(src_dir)

from dmnEvaluator import DMNEvaluator, DMNInputType
from dmnTable import DMNTable, DMNInput
from genericObject import GenericObject


class TestDMNFunctions(unittest.TestCase):

    def setUp(self):
        invoiceId = "a-bb1s2345678"
        orderId = "a-bb876s54321"
        self.order = GenericObject(clazz="order", id=orderId,totalamount=150, history=[], related_objects={"invoice": [invoiceId]})
        self.invoice = GenericObject(clazz="invoice", id=invoiceId, receiveDate=None, history=[], related_objects={"order": [orderId]})
        self.objects = [self.order, self.invoice]
        
        input0 = DMNInput("id", DMNInputType.attribute)
        input1 = DMNInput("totalamount", DMNInputType.attribute)
        input2 = DMNInput("invoice", DMNInputType.link)
        input3 = DMNInput("history",DMNInputType.history)
        
        self.orderDMN = DMNTable("order", [input0, input1, input2, input3])

        input0 = DMNInput("id", DMNInputType.attribute)
        input1 = DMNInput("receiveDate", DMNInputType.attribute)
        input2 = DMNInput("history",DMNInputType.history)
        
        self.invoiceDMN = DMNTable("invoice", [input0, input1, input2])
        
        dmnTables = [self.orderDMN, self.invoiceDMN]
                
        self.evaluator = DMNEvaluator(dmnTables, self.objects, debugging=True)
        
        
    def test_basicOperations(self):
        #add rules
        self.orderDMN.add_rule([None,"150",None,None])
        self.orderDMN.add_state("eq150")
        self.orderDMN.add_rule([None,"190",None,None])
        self.orderDMN.add_state("eq190")
        self.orderDMN.add_rule([None,"> 100",None,None])
        self.orderDMN.add_state("gr100")
        self.orderDMN.add_rule([None,"> 1000",None,None])
        self.orderDMN.add_state("gr1000")
        self.order.id = "327aqwsd"
        self.orderDMN.add_rule(["!= None",None,None,None])
        self.orderDMN.add_state("NotNone")

        # test rules
        states = self.evaluator.evaluate(self.order)
        self.assertIn("eq150", states)
        self.assertNotIn("eq190",states)
        self.assertIn("gr100", states)
        self.assertNotIn("gr1000",states)
        self.assertIn("NotNone",states)
    
    def test_historyFunctions(self):
        # add rules
        self.orderDMN.add_rule([None,None,None,"amount('CreateInvoice') == 1"])
        self.orderDMN.add_state("createInvoice")
        self.orderDMN.add_rule([None,None,None,"amount('ArchiveOrder') == 2"])
        self.orderDMN.add_state("archiveOrder")
                
        # test rules
        states = self.evaluator.evaluate(self.order)
        self.assertNotIn("createInvoice",states)
        self.assertNotIn("archiveOrder",states)
        self.order.history = ["CreateInvoice", "ArchiveOrder"]
        states = self.evaluator.evaluate(self.order)
        self.assertIn("createInvoice",states)
        self.assertNotIn("archiveOrder",states)
        self.order.history = ["CreateInvoice", "ArchiveOrder", "ArchiveOrder"]
        states = self.evaluator.evaluate(self.order)
        self.assertIn("createInvoice",states)
        self.assertIn("archiveOrder",states)

    def test_linkFunctionAmount(self):
        # add rules
        self.orderDMN.add_rule([None,None,"amount() > 0 ",None])
        self.orderDMN.add_state("invoicePresent")

        # test rules
        self.order.related_objects = {}
        states = self.evaluator.evaluate(self.order)
        self.assertNotIn("invoicePresent",states)
        self.order.related_objects['invoice'] = [self.invoice.id]
        states = self.evaluator.evaluate(self.order)
        self.assertIn("invoicePresent",states)

    def test_linkFunctionAmountWithState(self):
        #add rules
        self.orderDMN.add_rule([None,None,"amount('sent') > 0",None])
        self.orderDMN.add_state("invoiceSent")
        self.invoiceDMN.add_rule([None, None, "amount('SentInvoice') == 1"])
        self.invoiceDMN.add_state("sent")

        #test rules
        self.invoice.history = []
        states = self.evaluator.evaluate(self.order)
        self.assertNotIn("invoiceSent",states)
        self.invoice.history = ["SentInvoice"]
        states = self.evaluator.evaluate(self.order)
        self.assertIn("invoiceSent",states)

    def test_linkFunctions(self):
        # add rules
        self.invoiceDMN.add_rule([None,"== None",None])
        self.invoiceDMN.add_state("unpaid")
        self.invoiceDMN.add_rule([None,"!= None",None])
        self.invoiceDMN.add_state("paid")
        
        self.orderDMN.add_rule([None,None,"amount('paid') == 1",None])
        self.orderDMN.add_state("paid")
        self.orderDMN.add_rule([None,None,"amount('unpaid') == 1",None])
        self.orderDMN.add_state("unpaid")

        #test rules
        states = self.evaluator.evaluate(self.order)
        self.assertNotIn("paid",states)
        self.assertIn("unpaid",states)
        self.invoice.receiveDate = "2021-01-01"
        states = self.evaluator.evaluate(self.order)
        self.assertIn("paid",states)
        self.assertNotIn("unpaid",states)
        
    def test_linkFunction_exists(self):
        # add rules
        self.orderDMN.add_rule([None,None,"amount() == 1",None])
        self.orderDMN.add_state("invoiced")

        # test rules
        id = self.order.related_objects['invoice']
        self.order.related_objects = {}
        states = self.evaluator.evaluate(self.order)
        self.assertNotIn("invoiced",states)
        self.order.related_objects['invoice'] = id
        states = self.evaluator.evaluate(self.order)
        self.assertIn("invoiced",states)
        
    def test_crossStateEvaluation(self):
        # add rules
        self.invoiceDMN.add_rule([None,None,"amount('SentInvoice') == 1"])
        self.invoiceDMN.add_state("sent")
        
        self.orderDMN.add_rule([None,None,"amount('sent') == 1",None])
        self.orderDMN.add_state("invoiced")
        
        # test rules
        self.invoice.history = []
        states = self.evaluator.evaluate(self.order)
        self.assertNotIn("invoiced",states)
        
        self.invoice.history = ["SentInvoice"]
        states = self.evaluator.evaluate(self.order)
        self.assertIn("invoiced",states)
        
    def test_evaluationOfMultipleConditions(self):
        # add rules
        self.orderDMN.add_rule([None,"< 200 and > 100",None,None])
        self.orderDMN.add_state("between100and200")
        self.orderDMN.add_rule([None, None, None, "amount('SentPayment') == 1 or amount('AbortPayment') == 1"])
        self.orderDMN.add_state("paymentSentOrAbort")
        
        # test rules
        self.order.totalamount = 150
        self.order.history = []
        states = self.evaluator.evaluate(self.order)
        self.assertIn("between100and200",states)
        self.assertNotIn("paymentSentOrAbort",states)
        
        self.order.history = ["SentPayment"]
        self.order.totalamount = 50
        states = self.evaluator.evaluate(self.order)
        self.assertNotIn("between100and200",states)
        self.assertIn("paymentSentOrAbort",states)
        
        self.order.history = ["AbortPayment"]
        states = self.evaluator.evaluate(self.order)
        self.assertIn("paymentSentOrAbort",states)

    def test_extractOperatorAndValue(self):
        input = DMNInput("totalamount", DMNInputType.attribute)
        
        self.order.totalamount = 150
        condition = "100"
        expression = self.evaluator._getExpression(self.order, input, condition)
        self.assertEqual(expression, f"150 == {condition}")
        
        condition = "< 200"
        expression = self.evaluator._getExpression(self.order, input, condition)
        self.assertEqual(expression, f"150 {condition}")
        
        condition = "< 100 or < 200"
        expression = self.evaluator._getExpression(self.order, input, condition)
        self.assertEqual(expression, f"150 < 100 or 150 < 200")
        
        input = DMNInput("invoice", DMNInputType.link)
        
        condition = "amount()"
        expression = self.evaluator._getExpression(self.order, input, condition)
        self.assertEqual(expression, f"self.functions_link.amount(\'{self.order.id}\',\'invoice\')")
        
        condition = "amount(\'sent\') == 1 or amount(\'paid\') == 1"
        expression = self.evaluator._getExpression(self.order, input, condition)
        self.assertEqual(expression, f"self.functions_link.amount(\'{self.order.id}\',\'invoice\',\'sent\') == 1 or self.functions_link.amount(\'{self.order.id}\',\'invoice\',\'paid\') == 1")

        condition = "amount() == 0"
        expression = self.evaluator._getExpression(self.order, input, condition)
        self.assertEqual(expression, f"self.functions_link.amount(\'{self.order.id}\',\'invoice\') == 0")
        
        
    def test_evaluationOfComplexConditions(self):
        # add rules
        self.orderDMN.add_rule([None,None,"amount() == 0",None])
        self.orderDMN.add_state("invoiceNotPresent")
        self.orderDMN.add_rule([None,"not(> 200 and < 1000)",None,None])
        self.orderDMN.add_state("amountNotBetween200and1000")
        
        # test rules
        self.order.related_objects = {}
        self.order.totalamount = 150
        states = self.evaluator.evaluate(self.order)
        self.assertIn("invoiceNotPresent",states)
        self.assertIn("amountNotBetween200and1000",states)
        
        self.order.related_objects['invoice'] = [self.invoice.id]
        self.order.totalamount = 500
        states = self.evaluator.evaluate(self.order)
        self.assertNotIn("invoiceNotPresent",states)
        self.assertNotIn("amountNotBetween200and1000",states)
        

if __name__ == '__main__':    
    unittest.main()
    
    