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
        
        input0 = DMNInput("id",DMNInputType.object)
        input1 = DMNInput("totalamount",DMNInputType.object)
        input2 = DMNInput("invoice",DMNInputType.relation)
        input3 = DMNInput("history",DMNInputType.history)
        
        self.orderDMN = DMNTable("order", [input0, input1, input2, input3])

        input0 = DMNInput("id",DMNInputType.object)
        input1 = DMNInput("receiveDate",DMNInputType.object)
        input2 = DMNInput("history",DMNInputType.history)
        
        self.invoiceDMN = DMNTable("invoice", [input0, input1, input2])
        
        dmnTables = [self.orderDMN, self.invoiceDMN]
                
        self.evaluator = DMNEvaluator(dmnTables, self.objects, debugging=True)    
        
    def test_attribute_notNull(self):
        # set rule
        self.orderDMN.add_rule(["notNull()","notNull()",None,None]) 
        self.orderDMN.add_state("notNull")
        
        # test rules
        self.order.id = None
        states = self.evaluator.evaluate(self.order)
        self.assertNotIn("notNull",states)
        self.order.id = 123
        states = self.evaluator.evaluate(self.order)
        self.assertIn("notNull", states)
        
        
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
        self.orderDMN.add_rule([None,None,None,"exists('CreateInvoice')"])
        self.orderDMN.add_state("createInvoice")
        self.orderDMN.add_rule([None,None,None,"exists('ArchiveOrder')"])
        self.orderDMN.add_state("archiveOrder")
                
        # test rules
        states = self.evaluator.evaluate(self.order)
        self.assertNotIn("createInvoice",states)
        self.assertNotIn("archiveOrder",states)
        self.order.history = ["CreateInvoice", "ArchiveOrder"]
        states = self.evaluator.evaluate(self.order)
        self.assertIn("createInvoice",states)
        self.assertIn("archiveOrder",states)
        
    def test_relationFunctions(self):
        # add rules
        self.invoiceDMN.add_rule([None,"== None",None])
        self.invoiceDMN.add_state("unpaid")
        self.invoiceDMN.add_rule([None,"!= None",None])
        self.invoiceDMN.add_state("paid")
        
        self.orderDMN.add_rule([None,None,"inState('paid')",None])
        self.orderDMN.add_state("paid")
        self.orderDMN.add_rule([None,None,"inState('unpaid')",None])
        self.orderDMN.add_state("unpaid")

        #test rules
        states = self.evaluator.evaluate(self.order)
        self.assertNotIn("paid",states)
        self.assertIn("unpaid",states)
        self.invoice.receiveDate = "2021-01-01"
        states = self.evaluator.evaluate(self.order)
        self.assertIn("paid",states)
        self.assertNotIn("unpaid",states)
        
    def test_relationFunction_exists(self):
        # add rules
        self.orderDMN.add_rule([None,None,"exists()",None])
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
        self.invoiceDMN.add_rule([None,None,"exists('SentInvoice')"])
        self.invoiceDMN.add_state("sent")
        
        self.orderDMN.add_rule([None,None,"inState('sent')",None])
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
        self.orderDMN.add_rule([None, None, None, "exists('SentPayment') or exists('AbortPayment')"])
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
        input = DMNInput("totalamount",DMNInputType.object)
        
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
        
        input = DMNInput("invoice",DMNInputType.relation)
        
        condition = "exists()"
        expression = self.evaluator._getExpression(self.order, input, condition)
        self.assertEqual(expression, f"self.functions_relation.exists(\"{self.order.related_objects['invoice'][0]}\")")
        
        condition = "inState(\"sent\") or inState(\"paid\")"
        expression = self.evaluator._getExpression(self.order, input, condition)
        self.assertEqual(expression, f"self.functions_relation.inState(\"{self.order.related_objects['invoice']}\",\"sent\") or self.functions_relation.inState(\"{self.order.related_objects['invoice']}\",\"paid\")")

        condition = "not(exists())"
        expression = self.evaluator._getExpression(self.order, input, condition)
        self.assertEqual(expression, f"not(self.functions_relation.exists(\"{self.order.related_objects['invoice']}\"))")
        
        
    def test_evaluationOfComplexConditions(self):
        # add rules
        self.orderDMN.add_rule([None,None,"not(exists())",None])
        self.orderDMN.add_state("invoiceNotPresent")
        self.orderDMN.add_rule([None,"not(> 200 and < 1000)",None,None])
        self.orderDMN.add_state("amountNotBetween200and1000")
        
        # test rules
        self.order.related_objects = {}
        self.order.totalamount = 150
        states = self.evaluator.evaluate(self.order)
        self.assertIn("invoiceNotPresent",states)
        self.assertIn("amountNotBetween200and1000",states)
        
        self.order.related_objects['invoice'] = self.invoice.id
        self.order.totalamount = 500
        states = self.evaluator.evaluate(self.order)
        self.assertNotIn("invoiceNotPresent",states)
        self.assertNotIn("amountNotBetween200and1000",states)
        

if __name__ == '__main__':    
    unittest.main()
    
    