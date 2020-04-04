class P2f:
    def __init__(self,x=0,y=0):
        self.x, self.y = x,y
        
    def fromStr(self,dat):
        xy = dat.split(',')        
#         print(xy)
        self.x, self.y = float(xy[0]), float(xy[1])
        return self
    

    def addX(self,dx):
#         print(self.x, dx)
        self.x += dx
        return self
    
    def addY(self,dy): 
        self.y += dy
        return self
    
    def clone(self):
        return P2f(self.x,self.y)
    
    def dist(self,p2f):
        return np.sqrt((self.x-p2f.x)*(self.x-p2f.x) + (self.y-p2f.y)*(self.y-p2f.y))
    
class Line:
    def __init__(self,p1,p2):
        self.p1, self.p2 = p1,p2
        
    def clone(self):
        return Line(self.p1.clone(),self.p2.clone())
    
    def isVertical(self):
        return abs(self.p1.x - self.p2.x) < 1e-6
    
    def isHorizontal(self):
        return abs(self.p1.y - self.p2.y) < 1e-6
    
    def addX(self,dx):
        self.p1.addX(dx)
        self.p2.addX(dx)
        return self
    
    def addY(self,dy):
        self.p1.addY(dy)
        self.p2.addY(dy)
        return self
    
    def get2sides(self, width = 1.0):
        l1,l2 = self.clone(),self.clone()
#         if self.isVertical():
#             l1.addX(-width/2)
#             l2.addX(width/2)
#         elif self.isHorizontal():
#             l1.addY(-width/2)
#             l2.addY(width/2)
#         else:
        theta = math.atan2(self.p2.y - self.p1.y,self.p2.x-self.p1.x)
        dx = math.sin(theta)*width/2
        dy = math.cos(theta)*width/2
        l1.addX(-dx).addY(dy)
        l2.addX(dx).addY(-dy)
        return l1,l2
            
    def plot(self,plt,sym = 'r-'):
        plt.plot([self.p1.x, self.p2.x], [self.p1.y, self.p2.y], sym)
        
    def length(self):
        return self.p1.dist(self.p2)

def procData():
    lineData = """
    2.5,0 : 2.5,3.5
    4.5,0 : 4.5,2.5
    2.5,1.5 : 6,1.5
    0,2.5 : 3.5,2.5
    3.5,2.5 : 4.5,1.5
    3.5,2.5 : 5.5,4.5
    0, 4.5 : 6,4.5
    0.5,4.5 : 0.5,6
    3.5,4.5 : 3.5,6
    3.5,5.5 : 5.5,5.5
    5.5,5.5 : 5.5,6
    """
# 5.5,5.5 : 5.5,6
    lines = lineData.strip().split('\n')
    lineArray = []
    for l in lines:
        pts = l.split(':')
        p1,p2 = pts[0],pts[1]
    #     p1 = P2f().fromStr(p1.strip())
    #     p2 = P2f().fromStr(p2.strip())
    #     print(p1,p2)
        ln = Line(P2f().fromStr(p1.strip()), P2f().fromStr(p2.strip()))
        lineArray.append(ln)
    return lineArray


