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


scv = Build(50,20,0.7,0,1,[],"SCV")
marine = Build(50,24,0,0,1,["Barracks"],"Marine")
barracks = Factory(100,80,0,0,1,[],"Barracks")



def setBuildOrder(job):
    product = []

    def checkPrereq(partialSolution, prereqs):
        if not prereqs:
            return 1
        if not partialSolution:
            return 0
        if prereqs[0] in partialSolution:
            return checkPrereq(partialSolution, prereqs[1:])
        else:
            return 0

    def buildTrees(group, prod):
        if group==[]:
            product.append(prod)
            return
        for i in group:
            ngroup = group[:]

            #insertion
            if checkPrereq([x.type for x in prod],i[0].prereq):
                ngroup[ngroup.index(i)]=(i[0],i[1]-1) #delete from main stack
                nprod = prod[:]+[i[0]] #add to specific answer

                buildTrees([x for x in ngroup if x[1]>0],nprod)

    buildTrees(job,[])

    #helper function for factory queue filter
    def filterQueue(factory):
        if factory.queue == None:
            return 0
        else:
            return factory.queue.time

    def calculateTime(solution):
        cash = 50
        income = 0.0000001
        time = 0.0
        tempSol = []
        i = 0
        while i < len(solution):
            build = solution[i]
            if cash<build.cost:
                waitTime= float((build.cost-cash))/income
                time+=waitTime
                cash+=waitTime*income
            time+=build.time
            cash+=build.time*income
            cash-=build.cost
            income+=build.income
            tempSol.append(build)
            i+=1
        return time

    timeList = [(x, calculateTime(x)) for x in product]
    #for i in timeList[-10:-1]: print i
    return min(timeList, key=lambda x: x[1])

optimal = ([],100000)
for i in range(0,10):
    new = setBuildOrder([(marine,14),(barracks,1),(scv,i)])
    if new[1]<optimal[1]:
        optimal = new
print optimal

#TODO: special interface for multiple buildings.
#TODO: Supply.