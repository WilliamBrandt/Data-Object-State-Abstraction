import networkx as nx
import re
import matplotlib.pyplot as plt
from dmnTable import DMNTable
from dmnInputType import DMNInputType


class DMNGraph():
    def __init__(self, dmn_tables : list[DMNTable], debugging = False):
        self.debugging = debugging
        self.dmnTables = dmn_tables
        self.graph = nx.DiGraph()
        self._addNodesAndEdges()
        
    def _addNodesAndEdges(self):   
        for table in self.dmnTables:
            clazz = table.tablename
            for i, state in enumerate(table.states):
                currentNode = clazz + "." + state
                self.graph.add_node(currentNode)
                
                for j, input in enumerate(table.inputs):
                    if input.type == DMNInputType.state:
                        referedStates = self._extractStatesFromStateCondition(table.rules[i][j])
                        for referedState in referedStates:
                            nextNode = clazz + "." + referedState
                            self.graph.add_edge(currentNode, nextNode)  
                        
                    if input.type == DMNInputType.relation:
                        referedStates = self._extractStatesFromRelation(table.rules[i][j])
                        for referedState in referedStates:
                            nextNode =  input.label + "." + referedState
                            self.graph.add_edge(currentNode, nextNode)

    def _extractStatesFromStateCondition(self, stateCondition):   
        if stateCondition is None:
            return []
        replace = {"or": " ", "and": " ", "not": " ", "(": " ", ")": " "}
        for key in replace:
            stateCondition = stateCondition.replace(key, replace[key])
        return stateCondition.split()
    
    def _extractStatesFromRelation(self, relation):
        if relation is None:
            return []

        replace = {"'": "", "\"" : ""}
        for key in replace:
            relation = relation.replace(key, replace[key])

        pattern = r"amount\(([^']+)\)"
        match = re.search(pattern, relation)
        if match:
            return [match.group(1)]
        return []

    # Returns true if graph is cyclic else false
    def isCyclic(self):
        try:
            #Return: directed edges
            # Or Raises:NetworkXNoCycle
            nx.find_cycle(self.graph)
            return True
        except:
            return False
        
    def drawGraph(self):
        pos = nx.circular_layout(self.graph)
        nx.draw(self.graph,pos, with_labels=True, font_weight='bold')
        plt.show()