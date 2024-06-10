import unittest
from dmnEvaluator import DMNEvaluator, DMNInputType
from dmnTable import DMNTable, DMNInput
from genericObject import GenericObject

class TestDMNFunctions(unittest.TestCase):

    def setUp(self):
        self.order = GenericObject(clazz="order", id=None,totalamount=150, invoice="asda-21231-a21as", history=[])
        self.invoice = GenericObject(clazz="invoice", id="asda-21231-a21as", receiveDate=None, history=[])
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
        self.orderDMN.add_rule(["notNull()","notNull()",None]) 
        self.orderDMN.add_state("notNull")
        
        # test rules
        states = self.evaluator.evaluate(self.order)
        self.assertNotIn("notNull",states)
        self.order.id = 123
        states = self.evaluator.evaluate(self.order)
        self.assertIn("notNull", states)
        
        
    def test_basicOperations(self):
        #add rules
        self.orderDMN.add_rule([None,"150",None])
        self.orderDMN.add_state("eq150")
        self.orderDMN.add_rule([None,"190",None])
        self.orderDMN.add_state("eq190")
        self.orderDMN.add_rule([None,"> 100",None])
        self.orderDMN.add_state("gr100")
        self.orderDMN.add_rule([None,"> 1000",None])
        self.orderDMN.add_state("gr1000")
        self.order.id = "327aqwsd"
        self.orderDMN.add_rule(["!= None",None,None])
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
        id = self.order.invoice
        self.order.invoice = None
        states = self.evaluator.evaluate(self.order)
        self.assertNotIn("invoiced",states)
        self.order.invoice = id
        states = self.evaluator.evaluate(self.order)
        self.assertIn("invoiced",states)
        
    def test_crossStateEvaluation(self):
        # add rules
        self.invoiceDMN.add_rule([None,None,"exists('SentInvoice')",None])
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
        

if __name__ == '__main__':
    unittest.main()