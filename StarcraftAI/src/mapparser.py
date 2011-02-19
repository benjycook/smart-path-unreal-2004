
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