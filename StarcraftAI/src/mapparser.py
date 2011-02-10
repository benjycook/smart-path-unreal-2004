# To change this template, choose Tools | Templates
# and open the template in the editor.

from cPickle import *
from influenceMap import influenceMap

height = 128
width = 96
startLocations = [(8, 82), (116, 11)]

db = open("map.txt")
dots = load(db)
print dots
db.close()

#ROW MAJOR!!!

map=[[cell for cell in row] for row in dots]
#mapv=[[0 for cell in row] for row in dots]
for j in range(len(map)):
    for i in range(len(map[j])):
        color=[0,0,0]
        if map[j][i][0]: #buildable
            color[0]=128
        if map[j][i][1]: #walkable
            color[1]=128
        map[j][i]=color

infMap = influenceMap(width,height,2,64)
mapv = infMap.maprep
#calculate mapv
for j in range(len(map)):
    for i in range(len(map[j])):
        if map[j][i][1]: #walkable
            #is it buildable?
            if map[j][i][0]:
                mapv[i][j]=0
            else:
                mapv[i][j]=-16
            #is it an edge?
            if j==0 or i==0 or j==len(map)-2 or i==len(map[j])-1:
                mapv[i][j]+=32


infMap.calculateInfluence()
mapv = infMap.maprep

#display map
pres = open("map.html","w")
pres.write("<table border='0' cellpadding='0' cellspacing='0' style='font-size: 6px'>")
for i in range(width):
    pres.write("<tr>")
    for j in range(height):
        value = map[i][j]
        #value[2] = -mapv[i][j]
        color = "rgb("+str(value[0])+","+str(value[1])+","+str((mapv[j][i]+72)*value[0]/64)+")"
        pres.write("<td height='10' width='10' bgcolor='"+color+"'>"+str(mapv[j][i]))
        pres.write("</td>")
    pres.write("</tr>")

pres.write("</table>")
pres.close()
#TODO: connectivity graph to see which nodes are connected to start location
# center the search from the start location and branch out.