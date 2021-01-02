import random
from queue import Queue
import time
import datetime as dt

#blah blah balh balh

class Node:
    
    def __init__(self, value = None, children = [], state = None, level = 0):
        self._value = value
        self._children = children
        self._state = state
        self._level = level
    
    def __repr__(self):
        return ('score: ' + str(self._state.evaluate_board()) + '\n'
                +'level ' + str(self._level) + '\n'
                + str(self._state)
                )
    
    def min_value(self, node, alpha, beta):
        #print("Min Value")
        if node.is_terminal():
            return node.value
        value = float('inf')

        for elem in node.children:
            value = min(value, self.max_value(elem, alpha, beta))
            if value <= alpha:
                return value
            beta = min(beta, value)

        return value
    
    def max_value(self, node, alpha, beta):
        #print("Max Value")
        if node.is_terminal():
            return node.value
        value = -float('inf')

        for elem in node.children:
            value = max(value, self.min_value(elem, alpha, beta))
            if value >= beta:
                return value
            alpha = max(alpha, value)
            
        return value
    
    def alpha_beta_search(self):
        #print(self.children)
        best_val = -float('inf')
        beta = float('inf')

        best_state = None
        for elem in self.children:
            value = self.min_value(elem, best_val, beta)
            #time.sleep(1)
            #print(dt.datetime.now())
            #print(self)
            if value > best_val:
                best_val = value
                best_state = elem.state
        
        return best_state
    
    @property
    def children(self):
        return self._children
    
    @property
    def value(self):
        return self._value
    
    @property
    def state(self):
        return self._state

    @property
    def level(self):
        return self._level
    
    @children.setter
    def children(self, children):
        self._children = children
    
    @state.setter
    def state(self, state):
        self._state = state
    
    @value.setter
    def value(self, value):
        self._value = value

    def is_terminal(self):
        return len(self._children) == 0
        
def traverse_print(root):
    print(root.value)
    for tree in root.children:
        traverse_print(tree)

def level_order(root, level = 0):
    q = Queue(maxsize = 100)
    q.put(root)
    while not q.empty():
        curr_node = q.get()
        print(curr_node.value, curr_node.level)
        for idx, n in enumerate(curr_node.children):
            if idx == 0:
                level += 1
            q.put(n)
    return q

random.seed(0)

li = []
for x in range(8):
    li.append(random.randrange(1,100,1))

li = [2,3,5,9,0,1,7,5]

n0 = Node(li[0], level = 2)
n1 = Node(li[1], level = 2)
n2 = Node(li[2], level = 2)
n3 = Node(li[3], level = 2)
n4 = Node(li[4], level = 2)
n5 = Node(li[5], level = 2)
n6 = Node(li[6], level = 2)
n7 = Node(li[7], level = 2)

nodeA = Node(level = 0)
nodeB = Node(level = 1)
nodeC = Node(level = 1)
nodeD = Node(level = 1)
nodeE = Node(level = 1)
nodeF = Node(level = 1)
nodeG = Node(level = 1)

nodeA.children = [nodeB, nodeC]
nodeB.children = [nodeD, nodeE]
nodeC.children = [nodeF, nodeG]

nodeD.children = [n0, n1]
nodeE.children = [n2, n3]
nodeF.children = [n4, n5]
nodeG.children = [n6, n7]

#level_order(nodeA)