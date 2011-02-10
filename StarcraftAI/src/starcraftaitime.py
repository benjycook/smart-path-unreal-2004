# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="Benjy"
__date__ ="$Jan 23, 2011 11:11:56 PM$"

class Build:
    cost = 0
    time = 0
    income = 0.0
    supplyuse = 0
    supplyadd = 0
    prereq = []
    type = ""

    def __init__(self, cost, time, income, supplyuse, supplyadd, prereq, type):
        self.cost = cost
        self.time = time
        self.income = income
        self.supplyadd = supplyadd
        self.supplyuse = supplyuse
        self.prereq = prereq
        self.type = type


    def __repr__(self):
        return self.type

    def isFactory(self):
        return 0

    def buildable(self,listOfParents):
        stack = self.prereq[:]
        for i in listOfParents:
            if str(i.type) in stack: stack.remove(str(i.type))
        return not stack




class Factory(Build):
    queue = None
    def __init__(self, cost, time, income, supplyuse, supplyadd, prereq, type):
        self.cost = cost
        self.time = time
        self.income = income
        self.supplyadd = supplyadd
        self.supplyuse = supplyuse
        self.prereq = prereq
        self.type = type

    def isFactory(self):
        return 1

class Node():
    parents = []
    children = []
    type = None # class Build
    jobStack = None # job Stack class
    cost = 0
    cash = 0
    income = 0

    def __init__(self,parents,children,type,jobStack,cost):
        self.parents = parents
        self.children = children
        self.type = type
        self.jobStack = jobStack
        self.cost = cost

    def __repr__(self):
        return str(self.type)+str(self.jobStack)

class jobStack():
    itemStack = []
    quantityStack = []

    def __init__(self,itemStack,quantityStack):
        self.itemStack = itemStack
        self.quantityStack = quantityStack

    def removeItem(self,item):
        index = self.itemStack.index(item)
        self.quantityStack[index]-=1
        if self.quantityStack[index]==0:
            self.itemStack.remove(item)
            self.quantityStack.remove(self.quantityStack[index])

    def __repr__(self):
        return str(self.itemStack)+str(self.quantityStack)




scv = Build(50,20,0.7,0,1,[],"SCV")
marine = Build(50,24,0,0,1,["Barracks"],"Marine")
barracks = Factory(100,80,0,0,1,[],"Barracks")
commandcenter = Factory(100,80,0,0,1,[],"CommandCenter")


root = Node([],[],None,jobStack([scv,barracks,marine],[5,2,10]),0)
root.income = 1
root.cash = 50

def calculateIncome(node):
    if node.parents:
        node.income = node.parents[0].income
    if node.type.type=="SCV":
        node.income+=node.type.income

def calculateCosts(node):
    # do you need to wait for cash?
    # do you need to wait for a free factory?
    newTime = node.type.time
    if node.type!=None:
        if node.parents:
            node.cost = node.parents[0].cost+newTime
        else:
            node.cost = newTime
    else:
        node.cost = 0

def calculateCash(node):
    pass

def developNode(node):
    for item in node.jobStack.itemStack:
        newNode = Node([node]+node.parents,[],item,jobStack(node.jobStack.itemStack[:],node.jobStack.quantityStack[:]),0)
        newNode.jobStack.removeItem(item)
        calculateIncome(newNode)
        calculateCash(newNode)
        calculateCosts(newNode)
        node.children.append(newNode)

#developNode(root)

cnt=0
leaves = []
def traversal(node):
    global cnt
    global leaves
    cnt+=1
    if cnt>1000:
        return
    developNode(node)
    #print node
    for i in node.children:
        traversal(i)
    if not node.children:
        leaves.append(node)

traversal(root)

print [node.income for node in leaves]

