from math import log

class influenceMap:
    #row major, linear falloff
    width = 10
    height = 10
    falloff = 2
    maprep = []

    def __init__(self,width,height,falloff=2,maxV=100):
        self.width = width
        self.height = height
        self.falloff = falloff
        self.maxV = maxV
        self.maprep = [[0 for x in range(width)] for y in range(height)]

    def setValue(self,x,y,value):
        self.maprep[y][x] = value

    def calculateInfluence(self):
        features = [(x,y,self.maprep[y][x]) for x in range(self.width) for y in range(self.height) if self.maprep[y][x]!=0]
        tempMaps = [[self.maprep[y][:] for y in range(self.height)] for x in range(len(features))]
        for i in range(len(features)):
            feature = features[i]
            tempMap = tempMaps[i]
            maxSpread = int(log(abs(feature[2]),self.falloff))
            self.spread(feature[0],feature[1],maxSpread,tempMap)
        self.sumMaps(tempMaps)

    def sumMaps(self,graphs):
        newMap = [[0 for x in range(self.width)] for y in range(self.height)]
        for y in range(self.height):
            for x in range(self.width):
                for graph in graphs:
                    newMap[y][x]+=graph[y][x]
                    if newMap[y][x]<0:
                        newMap[y][x]=max(newMap[y][x],-self.maxV)
                    if newMap[y][x]>0:
                        newMap[y][x]=min(newMap[y][x],self.maxV)
        self.maprep = newMap
    
    def spread(self,x,y,dist,graph):
        value = self.maprep[y][x]
        for i in range(-dist,dist+1):
            for j in range(-dist,dist+1):
                if i==0 and j==0: continue
                if y+i>=self.height or x+j>=self.width: continue
                if y+i<0 or x+j<0: continue
                graph[y+i][x+j]=value/(2**max(abs(i),abs(j)))
        

    def __repr__(self):
        strrep = ""
        for y in range(self.height):
            strrep+=str(self.maprep[y])
            strrep+="\n"
        return strrep



#testing

#benjy = influenceMap(20,20)
#benjy.setValue(0,0,-64)
#benjy.setValue(10,5,64)
#benjy.calculateInfluence()
#print benjy
#
