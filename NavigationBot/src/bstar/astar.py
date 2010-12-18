#! /usr/bin/python
#Implemtation of astar

#TODO: Map Preproduction for cover and distances

__author__ = "Benjy"
__date__ = "$Nov 23, 2010 4:54:28 PM$"

r = navs.index(to)
s = navs.index(start)

weights = {"dist": 1.0 / float(maxdist),
    "health": 1, "ammo": 1,
    "adrenaline": 1,
    "weapons": 1, "cover": 1,
    "players": 1}

def betweenPoints(v1, v2, p):
    #TODO: Magic number?
    radius = 400 * 400
    denom = v1.getDistanceSquare(v2)
    top = (p.getX()-v1.getX()) * (v2.getX()-v1.getX())
    top += (p.getY()-v1.getY()) * (v2.getY()-v1.getY())
    top += (p.getZ()-v1.getZ()) * (v2.getZ()-v1.getZ())
    u = top / denom
    if u >= 0 and u <= 1:
        #closest point to sphere is on the line.
        x = v1.getX() + u * (v2.getX() - v1.getX()) - p.getX()
        y = v1.getY() + u * (v2.getY() - v1.getY()) - p.getY()
        z = v1.getZ() + u * (v2.getZ() - v1.getZ()) - p.getZ()
        if sum(x*x for x in [x,y,z]) <= radius:
            return True
    return False

def distance(a, b):
    return float(locations[a].getDistance(locations[b]))

def checkItem(a,b,itemType):
    checkList = [x[1] for x in bitems if x[0]==itemType]
    return sum([betweenPoints(a,b,itemLoc) for itemLoc in checkList])

def health(a, b):
    return (navitems[b] == "HEALTH") or checkItem(a,b,"HEALTH")

def adrenaline(a, b):
    return (navitems[b] == "ADRENALINE") or checkItem(a,b,"ADRENALINE")

def ammo(a, b):
    return (navitems[b] == "AMMO") or checkItem(a,b,"AMMO")

def weapons(a, b):
    return (navitems[b] == "WEAPON") or checkItem(a,b,"WEAPON")

def items(a, b):
    return sum([health(a, b) * weights["health"],
               adrenaline(a, b) * weights["adrenaline"],
               ammo(a, b) * weights["ammo"],
               weapons(a, b) * weights["weapons"]])

def cover(a, b):
    return 0

#How formidable an opponent the enemy is.
def enemyEvaluate(enemy):
    weaponScore = weaponsGrade[enemy.getWeapon().split(".")[1]] #0-10
    #if enemy.getTeam == me.getTeam:
    #    teamScore = -1
    #else:
    teamScore = 1
    print float(weaponScore+1 * teamScore)/11
    return float(weaponScore+1 * teamScore)/11


def players(a, b):
    pthreats = []
    for player in enemies:
        v1 = locations[a].getLocation()
        v2 = locations[b].getLocation()
        p = player.getLocation()
        if betweenPoints(v1, v2, p):
            pthreats.append(float(enemyEvaluate(player)))
    if len(pthreats) > 0:
        return float(sum(pthreats)) / len(pthreats)
    else:
        return 0 

#each segement is [0,1]
def g(a, b):
    gvars = [distance(a, b) * weights["dist"],
        items(a, b),
        cover(a, b) * weights["cover"],
        players(a, b) * weights["players"]]
    print sum(gvars)
    return sum(gvars)

def h(a, b):
    return 0#distance(a,b)

def f(v, r):
    return gcosts[v] + h(v, r)

parents = [None for x in range(len(navs))]
gcosts = [10000000 for x in range(len(navs))]

openl = []
closed = []
path = []

def aStar(s, r):
    gcosts[s] = 0
    openl.append(s)
    while openl:
        v = min(openl, key=lambda node:f(node, r)) #only place where h is
        if v == r: return parents
        openl.remove(v)
        for u in neighids[v]:
            if (parents[u] == None) or ((v in openl) and ((gcosts[v] + g(v, u)) < gcosts[u])):
                openl.append(u)
                gcosts[u] = gcosts[v] + g(v, u)
                parents[u] = v

aStar(s, r)

def findPath():
    c = r
    while c != s:
        path.append(c)
        c = parents[c]
    path.append(s)
    path.reverse()
    
findPath()

dist = [g(path[i], path[i + 1]) for i in range(len(path)-1)]
output = [locations[x] for x in path]
