#! /usr/bin/python

__author__="Benjy"
__date__ ="$Nov 23, 2010 4:54:28 PM$"

#This is passed to the main script every time the bot calls for pathfinding.

def itemToCategory(x):
    if not x.isInvSpot():
        return False
    else:
        return x.getItemClass().getCategory().toString()

def freeitemToCategory(items):
    newlist = []
    for x in items:
        if x.isDropped():
            newlist.append([x.getType().getCategory().toString(),x.getLocation()])
    return newlist


# what is passed to python?
# 1)    The NavGraph - Including Type A Items
# 2)    Players - locations array
# 3)    Type B Items

ids = [x.getId() for x in navs]
neighbors = [x.getOutgoingEdges() for x in navs]
neighids = [[ids.index(y) for y in [x.getId() for x in neighbors[i].values()]] for i in range(len(navs))]
navitems = [itemToCategory(x) for x in navs] #HEALTH, AMMO, WEAPON, False
bitems = freeitemToCategory(items)
locations = [x.getLocation() for x in navs]



#graded by planet unreal Weapons Guide
weaponsGrade = { "AssaultRifle": 2,
            "ShieldGun": 1,
            "FlakCannon": 7,
            "BioRifle": 5,  
            "ShockRifle": 4,
            "SniperRifle": 9,
            "RocketLauncher": 8,
            "Minigun": 6,
            "LightingGun": 10,
            "Translocator": 0,
            "LinkGun": 3}

if len(players)>0:
    enemies=[x for x in players if x.getLocation()!=None]
else:
    enemies=[]
maxdist = 500

lastItems = items

if me!=None:
    me = {"health": me.getHealth(), "adrenaline":me.getAdrenaline(),
    "team": me.getTeam(), "ammo": me.getPrimaryAmmo()}
else:
    me = {"health": 100, "adrenaline":0, "team": 0, "ammo": 50}

me["maxammo"] = 300

#TODO: Magic number: What is longest distance between 2 neighboring wp in map?
#TODO: Maximum ammo for all weapons
