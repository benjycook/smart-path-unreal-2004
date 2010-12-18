#! /usr/bin/python
#Implemtation of astar

#TODO: Map Preproduction for cover and distances
#TODO: Pass the following to python:    Bot Health, Weapons
#                                       Other Bots State - Friend/Foe, Health, Weapons
#                                       

#TODO: Ideas: A strategic bot analysis function, which recieves a bot and returns how much of a threat it is. [-100, 100]

__author__="Benjy"
__date__ ="$Nov 23, 2010 4:54:28 PM$"

r = navs.index(to)
s = navs.index(start)

weights = { "dist": float(1/maxdist),
            "health": 1, "ammo": 1,
            "adrenaline": 1,
            "weapons": 1, "cover": 1,
            "players": 1}

def distance(a,b):
    return locations[a].getDistance(locations[b])

def health(a,b):
    return (navitems[b]=="HEALTH")

def adrenaline(a,b):
    return (navitems[b]=="ADRENALINE")

def ammo(a,b):
    return (navitems[b]=="AMMO")

def weapons(a,b):
    return (navitems[b]=="WEAPON")

def items(a,b):
    return sum([health(a,b)*weights["health"],
                adrenaline(a,b)*weights["adrenaline"],
                ammo(a,b)*weights["ammo"],
                weapons(a,b)*weights["weapons"]])

def cover(a,b):
    return 1

def players(a,b):
    if len(plocs)>0:
        pthreats=[]
        for player in plocs:
            pthreats.append(1)
        return sum(pthreats)/len(pthreats)
    else:
        return 0

#each segement is [0,1]
def g(a,b):
    return sum([distance(a,b)*weights["dist"],
                items(a,b),
                cover(a,b)*weights["cover"],
                players(a,b)*weights["players"]])

def h(a,b):
    return 0#distance(a,b)

def f(v,r):
    return gcosts[v]+h(v,r)

parents = [None for x in range(len(navs))]
gcosts = [10000000 for x in range(len(navs))]

openl = []
closed = []
path = []

def aStar(s,r):
    gcosts[s]=0
    openl.append(s)
    while openl:
        v = min(openl, key=lambda node:f(node,r)) #only place where h is
        if v==r: return parents
        openl.remove(v)
        for u in neighids[v]:
            if (parents[u]==None) or ((v in openl) and ((gcosts[v]+g(v,u)) < gcosts[u])):
                openl.append(u)
                gcosts[u]=gcosts[v]+g(v,u)
                parents[u]=v

aStar(s,r)

def findPath():
    c = r
    while c!=s:
        path.append(c)
        c=parents[c]
    path.append(s)
    path.reverse()
    
findPath()
#print [ids[i] for i in path]
dist = [g(path[i],path[i+1]) for i in range(len(path)-1)]


#fil = open("c:/log2.txt","a")
#fil.write(str(sum(ite))+"\n")
#fil.close()
output = [locations[x] for x in path]
