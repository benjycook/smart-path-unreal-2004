from numpy import *
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
print baseMap.shape

colorDict = {Feature.AIR : "grey", Feature.BUILDABLE : "white",
            Feature.MAP_EDGE : "blue", Feature.GND_EDGE : "red",
            Feature.AIR_EDGE : "cyan", Feature.START_LOC : "pink"}

pres = open("map.html","w")
pres.write("<table border='1' cellpadding='0' cellspacing='0' style='font-size: 5px'>")
for i in range(HEIGHT):
    pres.write("<tr>")
    for j in range(WIDTH):
        value = baseMap[j,i]
        color = colorDict[value]
        pres.write("<td height='10' width='10' bgcolor='"+color+"' align='center'>"+str(baseMap[j,i]))
        pres.write("</td>")
    pres.write("</tr>")

pres.write("</table>")
pres.write("<pre>")
pres.write("AIR black    ")
pres.write("BUILDABLE white    ")
pres.write("MAP_EDGE blue    ")
pres.write("GND_EDGE red    ")
pres.write("AIR_EDGE cyan")

                
        
