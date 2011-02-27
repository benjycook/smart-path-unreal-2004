from numpy import *
from math import hypot
from cPickle import *

class Feature:
        AIR=0
        WALKABLE=-1
        BUILDABLE=-2
        MAP_EDGE=-4
        GND_EDGE=-8
        AIR_EDGE=-16
        BUILDING=-32
        START_LOC=-64
        NULL=-256

WIDTH = 128
HEIGHT = 96
STARTLOCATION = (8, 82)
BASIC_SIZE = 4

f=open("map.txt")
data=load(f) # row major, each cell tuple, boolean (buildable, walkable)
f.close()

# Create an empty map
map = zeros((WIDTH,HEIGHT),dtype=int32)

# Set each cell to a corresponding feature type: A=0,B=2,W=1
for j in range(HEIGHT):
        for i in range(WIDTH):
                buildable = data[j][i][0]
                walkable = data[j][i][1]
                if buildable:
                        map[i,j]=Feature.BUILDABLE
                elif walkable:
                        map[i,j]=Feature.WALKABLE

#Flood from start Location

def lookAtNeighbors(mapData,cell): #array type, coord tuple
        #OUT: celltype, any neighbors
# is it a map edge?
        cellType=False
        mapEdge=False
        airEdge=False
        gndEdge=False
        buildable=False
        x = cell[0]
        y = cell[1]
        neighbors=[]
        if x<=2 or x>=WIDTH-2 or y<=2 or y>=HEIGHT-2:
                mapEdge=True
        else:
                north, south = mapData[x,y-1], mapData[x,y+1]
                east, west = mapData[x-1,y], mapData[x+1,y]
                airEdge = (north == Feature.AIR or south == Feature.AIR or east == Feature.AIR or west == Feature.AIR)
                gndEdge = (north == Feature.WALKABLE or south == Feature.WALKABLE or west == Feature.WALKABLE or east == Feature.WALKABLE)
                if north == Feature.BUILDABLE: neighbors.append((x,y-1))
                if east == Feature.BUILDABLE: neighbors.append((x-1,y))
                if west == Feature.BUILDABLE: neighbors.append((x+1,y))
                if south == Feature.BUILDABLE: neighbors.append((x,y+1))
        if mapEdge:
            celltype = Feature.MAP_EDGE
        elif gndEdge:
            celltype = Feature.GND_EDGE
        elif airEdge:
            celltype = Feature.AIR_EDGE
        else:
            celltype = Feature.BUILDABLE
        return celltype, neighbors
                 
        
def flood(mapData):
    openlist = [STARTLOCATION]
    closedlist = []
    newMap = zeros((WIDTH,HEIGHT),dtype=int32)
    while openlist:
        cellc = openlist.pop()
        if cellc in closedlist: continue
        celltype, neighbors = lookAtNeighbors(mapData,cellc)
        if cellc == STARTLOCATION: celltype = Feature.START_LOC
        newMap[cellc[0],cellc[1]]=celltype
        openlist+=neighbors
        closedlist.append(cellc)

    return newMap#[x1:x2,y1:y2]


baseMap = flood(map)


## calculate influence.
def influence(map, featureDict):
    # @type map array
    featureSet = [(map[i,j],i,j) for i in range(WIDTH) for j in range (HEIGHT) if map[i,j] in featureDict.keys()]
    newMap = zeros((WIDTH,HEIGHT),dtype=int32)
    for i in range(WIDTH):
        for j in range(HEIGHT):
            if map[i,j]==Feature.BUILDABLE:
                for feature in featureSet:
                    newMap[i,j]+=calcInfluence(feature[1:],(i,j),featureDict[feature[0]])
    return newMap

def calcInfluence((x1,y1),(x2,y2),(initialValue,falloff)):
    dist = hypot(x2-x1,y2-y1)
    return initialValue/(falloff**dist)

maps = {}
sumMaps = {}
def createMaps():
    global basicBuildings
    global defenseBuildings
    global airBuildings
    global supplyBuildings
    global maps
    global sumMaps
    basicBuildings = influence(baseMap,{Feature.START_LOC: (512,1.3), Feature.GND_EDGE: (-64,2), Feature.AIR_EDGE: (-64,2), Feature.MAP_EDGE: (-64,2)})
    defenseBuildings = influence(baseMap,{Feature.START_LOC: (-512,2), Feature.GND_EDGE: (512,3), Feature.AIR_EDGE: (-64,2), Feature.MAP_EDGE: (-64,2)})
    airBuildings = influence(baseMap,{Feature.START_LOC: (-512,3), Feature.GND_EDGE: (-64,3), Feature.AIR_EDGE: (512,3), Feature.MAP_EDGE: (-128,2)})
    supplyBuildings = influence(baseMap,{Feature.START_LOC: (-1024,7), Feature.GND_EDGE: (-128,4), Feature.AIR_EDGE: (-128,4), Feature.MAP_EDGE: (-128,4)})
    maps = {"basic": basicBuildings, "gndDefense": defenseBuildings, "airDefense": airBuildings, "supply": supplyBuildings}
    for map in maps.keys():
        sumMaps[map]=sumMap(maps[map])


def sumMap(map):
    newMap = zeros((WIDTH,HEIGHT),dtype=int32)
    for x in range(WIDTH):
        for y in range(HEIGHT):
            fourValue = sum(map[x-BASIC_SIZE:x,y-BASIC_SIZE:y].flat)
            buildable = True
            buildsum = sum(baseMap[x-BASIC_SIZE:x,y-BASIC_SIZE:y].flat)
            buildable = buildsum==Feature.BUILDABLE*(BASIC_SIZE**2)
            if buildable:
                newMap[x,y] = fourValue
            else:
                newMap[x,y] = -255
    return newMap

def printMap(map):
    max = map.max()
    min = map.min()

    pres = open("map.html","w")
    pres.write("<table border='1' cellpadding='0' cellspacing='0' style='font-size: 6px'>")
    for i in range(HEIGHT):
        pres.write("<tr height='15'>")
        for j in range(WIDTH):
            if baseMap[j,i]==Feature.BUILDABLE:
                value = map[j,i]
                if max!=min:
                    colorValue = float(value-min)/(max-min)
                    colorValue = str(int(colorValue*255))
                else:
                    colorValue = "0"
                
                color = "rgb("+colorValue+","+colorValue+","+colorValue+")"
                pres.write("<td height='14' width='18' align='center' bgcolor='"+color+"'>"+str(value))
                pres.write("</td>")
            elif baseMap[j,i]==Feature.START_LOC:
                pres.write("<td height='14' width='18' align='center' bgcolor='blue'>")
                pres.write("</td>")
            else:
                pres.write("<td height='14' width='18' align='center' bgcolor='cyan'>")
                pres.write("</td>")
        pres.write("</tr>")

    pres.write("</table>")

def bestPlaceToBuild(typeOfBuilding):
    map = sumMaps[typeOfBuilding]
    m = map.max()
    bestPlace = [x for x in where(map == m)]
    for i in range(len(bestPlace[0])):
        x=bestPlace[0][i]
        y=bestPlace[1][i]
        if sum(baseMap[x-BASIC_SIZE:x,y-BASIC_SIZE:y])==Feature.BUILDABLE*(BASIC_SIZE**2):
            firstBestPlace = bestPlace[0][i], bestPlace[1][i]
            break
    return firstBestPlace

#createMaps()

def updateBuilding((x,y)):
    global baseMap
    for i in range(x-BASIC_SIZE,x):
        for j in range(y-BASIC_SIZE,y):
            baseMap[i,j] = Feature.BUILDING
    createMaps()

#printMap(baseMap)
#
#set_printoptions(threshold=nan)
#
#print baseMap[25:,80:]

import cProfile
cProfile.run('createMaps()')