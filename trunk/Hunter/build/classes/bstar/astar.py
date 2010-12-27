#! /usr/bin/python
#Implemtation of astar

__author__ = "Benjy Cook 301173084"
__date__ = "$Nov 23, 2010 4:54:28 PM$"

r = navs.index(to)
s = navs.index(start)

weights = {"dist": 5.0 / float(maxdist),
    "health": 1.0, "ammo": 1.0,
    "adrenaline": 1.0,
    "weapons": 1.0, "cover": 1.0,
    "players": 1.0}

def updateWeights():
    """
    Updates the weights dictionary for all various weights
    """
    weights["health"] = 1-(float(me["health"])/200)
    weights["adrenaline"] = 1-(float(me["adrenaline"])/100)
    weights["ammo"] = 1-(float(me["ammo"])/weaponsGrade[me["weapon"]][1])
    weights["players"] = (weights["health"]+weights["ammo"])*0.5

def betweenPoints(v1, v2, p):
    """
    Very useful predicate wheter feature p lies between v1 and v2.
    """
    radius = 400 * 400
    denom = v1.getDistanceSquare(v2)
    top = (p.getX()-v1.getX()) * (v2.getX()-v1.getX())
    top += (p.getY()-v1.getY()) * (v2.getY()-v1.getY())
    top += (p.getZ()-v1.getZ()) * (v2.getZ()-v1.getZ())
    if denom!=0:
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
    """
    Returns the distance between a and b
    """
    return float(locations[a].getDistance(locations[b]))

def checkItem(a,b,itemType):
    """
    Returns how many features of type itemType lie in between a and b
    Only used for items of type b, i.e. dropped items.
    """
    checkList = [x[1] for x in bitems if x[0]==itemType]
    return sum([betweenPoints(locations[a],locations[b],itemLoc) for itemLoc in checkList])

def health(a, b):
    """
    Predicate. Returns if any health power ups are between a-b, or on b.
    """
    return (navitems[b] == "HEALTH") or checkItem(a,b,"HEALTH")

def adrenaline(a, b):
    """
    Predicate. Returns if any Adrenaline power ups are between a-b, or on b.
    """
    return (navitems[b] == "ADRENALINE") or checkItem(a,b,"ADRENALINE")

def ammo(a, b):
    """
    Predicate. Returns if any ammo power ups are between a-b, or on b.
    """
    return (navitems[b] == "AMMO") or checkItem(a,b,"AMMO")

def weapons(a, b):
    """
    Predicate. Returns if any weapon power ups are between a-b, or on b.
    """
    return (navitems[b] == "WEAPON") or checkItem(a,b,"WEAPON")

def items(a, b):
    """
    A small weighted average function that collects all different items into
    a single number. Result is within [0,4].
    """
    return sum([health(a, b) * weights["health"],
               adrenaline(a, b) * weights["adrenaline"],
               ammo(a, b) * weights["ammo"],
               weapons(a, b) * weights["weapons"]])

def cover(a, b):
    """
    Never implemented due to time constraints. Original plan called for map
    precalculation, that would use the outlying geometry to analyze the different
    navpoints. Such an interface for map precalc/storing offline files would require
    a major restructuring of the code.
    """
    return 0

def enemyEvaluate(other):
    """
    Returns how formidable an opponent the bot 'other' is. Can also denote
    team mate, in which case that feature becomes an attractor, not a repulser.
    """
    weaponScore = weaponsGrade[other.getWeapon().split(".")[1]][0] #0-10
    if other.getTeam() == me["team"]:
        teamScore = -1
    else:
        teamScore = 1
    return float(weaponScore+1 * teamScore)/11


def players(a, b):
    """
    returns the sum of player-based threats between points a and b.
    Does so by iterating over all players and evaluating them, then sums.
    """
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

def g(a, b):
    """
    Function g of A*.
    """
    gvars = [distance(a, b) * weights["dist"],
        items(a, b),
        cover(a, b) * weights["cover"],
        players(a, b) * weights["players"]]
    return sum(gvars)

def h(a, b):
    """
    Heurisitic h of A*.
    This is an admissible heurisitic, with average 75% accuracy.
    Only items and players are "guesses".
    One should note that average 75% accuracy is typical of what is considered
    a good heuristic - air-distance in regular pathplanning.
    """
    hvars = [distance(a,b) * weights["dist"],
        items(a, b),
        cover(a, b) * weights["cover"],
        players(a, b) * weights["players"]]
    return sum(hvars)

def f(v, r):
    """
    A*'s evaluator. Just g + h.
    """
    return gcosts[v] + h(v, r)


### Begin standard implemtation of A*.
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



updateWeights()

aStar(s, r)

def findPath():
    c = r
    while c != s:
        path.append(c)
        c = parents[c]
    path.append(s)
    path.reverse()
    
findPath()

output = [locations[x] for x in path]
