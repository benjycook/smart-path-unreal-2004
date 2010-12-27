#! /usr/bin/python

__author__ = "Benjy Cook 301173084"
__date__ ="$Nov 23, 2010 4:54:28 PM$"

#This is passed to the main script every time the bot calls for pathfinding.

def itemToCategory(x):
    """
    Recieves navpoint x and returns what type of item it has.
    False if not an item spot.
    """
    if not x.isInvSpot():
        return False
    else:
        return x.getItemClass().getCategory().toString()

def freeitemToCategory(items):
    """
    recieves list of all items and filters it to only dropped items.
    Returned list is composed of tuples, (String: ItemType, Location: Coordinates).
    """
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


#graded by Planet Unreal Weapons Guide
#http://planetunreal.gamespy.com/View.php?view=UT2004GameInfo.Detail&id=26&game=4
#and Beyond Unreal weapons Guide
#http://liandri.beyondunreal.com/Unreal_Tournament_2004#Weapons
weaponsGrade = { "AssaultRifle": (2,200),
            "ShieldGun": (1,100),
            "FlakCannon": (7,35),
            "BioRifle": (5,50),
            "ShockRifle": (4,50),
            "SniperRifle": (9,35),
            "RocketLauncher": (8,30),
            "Minigun": (6,300),
            "LightingGun": (10,40),
            "Translocator": (0,6),
            "LinkGun": (3,220)}

#Creates other bots list.
if len(players)>0:
    enemies=[x for x in players if x.getLocation()!=None]
else:
    enemies=[]

#constant used for normalizing distances.
maxdist = 500

lastItems = items

# me dictionary - holds our bot's updated status.
if me!=None:
    me = {"health": me.getHealth(), "adrenaline":me.getAdrenaline(),
    "team": me.getTeam(), "ammo": me.getPrimaryAmmo(), "weapon": me.getWeapon().toString().split(".")[1][:-1]}
else:
    me = {"health": 100, "adrenaline":0, "team": 0, "ammo": 50}
