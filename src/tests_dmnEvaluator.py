import unittest
from dmnEvaluator import DMNEvaluator, DMNInputType
from dmnTable import DMNTable, DMNInput
from genericObject import GenericObject

class TestDMNFunctions(unittest.TestCase):

    def setUp(self):
        self.order = GenericObject(id=None,totalamount=150, invoice="asda-21231-a21as", history=[])
        self.invoice = GenericObject(id="asda-21231-a21as", state="sent")
        self.objects = [self.order, self.invoice]
        
        input0 = DMNInput("id",DMNInputType.object)
        input1 = DMNInput("totalamount",DMNInputType.object)
        input2 = DMNInput("invoice",DMNInputType.relation)
        input3 = DMNInput("history",DMNInputType.history)
        
        self.table = DMNTable("order", [input0, input1, input2, input3])
        self.evaluator = DMNEvaluator(self.table, self.objects, debugging=True)
        
    def test_attribute_notNull(self):
        # set rule
        self.table.add_rule(["notNull()","notNull()",None]) 
        self.table.add_state("notNull")
        
        # test rules
        states = self.evaluator.evaluate(self.order)
        self.assertNotIn("notNull",states)
        self.order.id = 123
        states = self.evaluator.evaluate(self.order)
        self.assertIn("notNull", states)
        
        
    def test_basicOperations(self):
        #add rules
        self.table.add_rule([None,"150",None])
        self.table.add_state("eq150")
        self.table.add_rule([None,"190",None])
        self.table.add_state("eq190")
        self.table.add_rule([None,"> 100",None])
        self.table.add_state("gr100")
        self.table.add_rule([None,"> 1000",None])
        self.table.add_state("gr1000")
        self.order.id = "327aqwsd"
        self.table.add_rule(["!= None",None,None])
        self.table.add_state("NotNone")
                
        # test rules
        states = self.evaluator.evaluate(self.order)
        self.assertIn("eq150", states)
        self.assertNotIn("eq190",states)
        self.assertIn("gr100", states)
        self.assertNotIn("gr1000",states)
        self.assertIn("NotNone",states)
    
    def test_historyFunctions(self):
        # add rules
        self.table.add_rule([None,None,None,"exists('CreateInvoice')"])
        self.table.add_state("createInvoice")
        self.table.add_rule([None,None,None,"exists('ArchiveOrder')"])
        self.table.add_state("archiveOrder")
                
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
        self.table.add_rule([None,None,"inState('paid')",None])
        self.table.add_state("paid")
        self.table.add_rule([None,None,"inState('unpaid')",None])
        self.table.add_state("unpaid")

        #test rules
        self.invoice.state = "sent"
        states = self.evaluator.evaluate(self.order)
        self.assertNotIn("paid",states)
        self.assertNotIn("unpaid",states)
        self.invoice.state = "paid"
        states = self.evaluator.evaluate(self.order)
        self.assertIn("paid",states)
        self.assertNotIn("unpaid",states)
        
    def test_relationFunction_exists(self):
        # add rules
        self.table.add_rule([None,None,"exists()",None])
        self.table.add_state("invoiced")

        # test rules
        id = self.order.invoice
        self.order.invoice = None
        states = self.evaluator.evaluate(self.order)
        self.assertNotIn("invoiced",states)
        self.order.invoice = id
        states = self.evaluator.evaluate(self.order)
        self.assertIn("invoiced",states)

if __name__ == '__main__':
    unittest.main()