import unittest
import sys
import os

# Calculate the path to the src directory relative to this file's location
current_dir = os.path.dirname(__file__)
src_dir = os.path.join(current_dir, '..')
src_dir = os.path.abspath(src_dir)

# Add the src directory to sys.path to make the imports work
sys.path.append(src_dir)

from dmnGraph import DMNGraph
from dmnTable import DMNTable, DMNInput
from dmnInputType import DMNInputType


class TestDMNFunctions(unittest.TestCase):

    def setUp(self):
        input0 = DMNInput("state",DMNInputType.state)
        input1 = DMNInput("id", DMNInputType.attribute)
        input2 = DMNInput("invoice", DMNInputType.link)
        
        self.orderDMN = DMNTable("order", [input0, input1, input2])
        
        input0 = DMNInput("state",DMNInputType.state)
        input1 = DMNInput("id", DMNInputType.attribute)
        input2 = DMNInput("order", DMNInputType.link)
        
        self.invoiceDMN = DMNTable("invoice", [input0, input1,input2])
    
    def _getGraph(self):
        return  DMNGraph([self.orderDMN, self.invoiceDMN], debugging=True)
    
    
    def test_noCycle(self):
        # add rules (no cycle)
        self.orderDMN.add_rule(["B",None,None]) 
        self.orderDMN.add_state("A")
        self.orderDMN.add_rule(["B",None,None])
        self.orderDMN.add_state("C")
        #test
        graph = self._getGraph()        
        self.assertFalse(graph.isCyclic())
    
    def test_cycle(self):
        # add rules (cycle)
        self.orderDMN.add_rule(["B",None,None]) 
        self.orderDMN.add_state("A")
        self.orderDMN.add_rule(["A",None,None])
        self.orderDMN.add_state("B")
        #test
        graph = self._getGraph()        
        self.assertTrue(graph.isCyclic())
        
    def test_complexCycle(self):
        # add rules 
        self.orderDMN.add_rule(["B or C",None,None])
        self.orderDMN.add_state("A")
        self.orderDMN.add_rule(["A",None,None])
        self.orderDMN.add_state("B")
        self.orderDMN.add_rule(["B",None,None])
        self.orderDMN.add_state("C")
        
        graph = self._getGraph()
        self.assertTrue(graph.isCyclic())
        
    def test_extractStates(self):
        graph = self._getGraph()
        self.assertEqual(graph._extractStatesFromStateCondition("A"), ["A"])
        self.assertEqual(graph._extractStatesFromStateCondition("A or B"), ["A", "B"])
        self.assertEqual(graph._extractStatesFromStateCondition("A and not(B)"), ["A", "B"])
        
    def test_linkCycle(self):
        # add rules 
        self.orderDMN.add_rule([None,None,"amount('B') == 1"])
        self.orderDMN.add_state("A")
        self.invoiceDMN.add_rule([None,None,"amount('A') == 1"])
        self.invoiceDMN.add_state("B")
        
        graph = self._getGraph()
        self.assertTrue(graph.isCyclic())
        
    def test_complexLinkCycle(self):
        # add rules 
        self.orderDMN.add_rule([None,None,"amount('B') == 1"])
        self.orderDMN.add_state("A")
        self.orderDMN.add_rule(["A",None,None])
        self.orderDMN.add_state("D")
        self.invoiceDMN.add_rule([None,None,"amount('D') == 1"])
        self.invoiceDMN.add_state("C")
        self.invoiceDMN.add_rule(["A or C",None,None])
        self.invoiceDMN.add_state("B")
        
        graph = self._getGraph()
        self.assertTrue(graph.isCyclic())

    def test_extractStatesFromLink(self):
        graph = self._getGraph()
        self.assertEqual(graph._extractStatesFromLink("amount('C') == 1"), ['C'])
        self.assertEqual(graph._extractStatesFromLink("amount(\"C\") == 1"), ['C'])
        self.assertEqual(graph._extractStatesFromLink("amount() == 1"), [])

        
if __name__ == '__main__':    
    unittest.main()
    
    