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

#set_printoptions(threshold=nan)
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

def calcInfluence((x1,y1),(x2,y2),(initalValue,falloff)):
    dist = hypot(x2-x1,y2-y1)
    return initalValue/(falloff**dist)

def createMaps():
    global basicBuildings
    global defenseBuildings
    global airBuildings
    basicBuildings = influence(baseMap,{Feature.START_LOC: (512,1.3), Feature.GND_EDGE: (-64,2), Feature.AIR_EDGE: (-64,2), Feature.MAP_EDGE: (-64,2)})
    defenseBuildings = influence(baseMap,{Feature.START_LOC: (-512,2), Feature.GND_EDGE: (512,3), Feature.AIR_EDGE: (-64,2), Feature.MAP_EDGE: (-64,2)})
    airBuildings = influence(baseMap,{Feature.START_LOC: (-512,3), Feature.GND_EDGE: (-64,3), Feature.AIR_EDGE: (512,3), Feature.MAP_EDGE: (-128,2)})

createMaps()

def sumMap(map):
    newMap = zeros((WIDTH,HEIGHT),dtype=int32)
    for x in range(WIDTH-4):
        for y in range(HEIGHT-4):
            fourValue = sum(map[x:x+4,y:y+4].flat)
            buildable = True
            for elem in baseMap[x:x+4,y:y+4].flat:
                if not elem==Feature.BUILDABLE:
                    buildable = False
                    break
            if buildable:
                newMap[x,y] = fourValue
    return newMap

def printMap(map):
    colorDict = {Feature.AIR : "grey", Feature.BUILDABLE : "white",
                Feature.MAP_EDGE : "blue", Feature.GND_EDGE : "red",
                Feature.AIR_EDGE : "cyan", Feature.START_LOC : "pink"}

    pres = open("map.html","w")
    pres.write("<table border='1' cellpadding='0' cellspacing='0' style='font-size: 6px'>")
    for i in range(HEIGHT):
        pres.write("<tr height='15'>")
        for j in range(WIDTH):
            if baseMap[j,i]==Feature.BUILDABLE:
                value = map[j,i]
                colorValue = str(value)
                color = "rgb("+colorValue+","+colorValue+","+colorValue+")"
                pres.write("<td height='15' width='15' align='center' bgcolor='"+color+"'>"+str(value))
                pres.write("</td>")
            else:
                pres.write("<td height='15' width='15' align='center' bgcolor='pink'>")
                pres.write("</td>")
        pres.write("</tr>")

    pres.write("</table>")

#printMap(sumMap(defenseBuildings))

myMap = sumMap(defenseBuildings)
m = myMap.max()
bestPlace = [int(x[0]) for x in where(myMap == m)]
print bestPlace
