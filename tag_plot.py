from math import atan2,pi
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge, Polygon
from matplotlib.collections import PatchCollection

class TagPozyx:
    def __init__(self,r=1,tip=3,dt=pi/3,theta0 = 0):
        self.r, self.tip, self.dt = r,tip,dt
        self.theta0 = theta0
        _, self.ax = plt.subplots()
        

    def preShow(self):
        plt.ion()
        plt.show()
        return self

        
    def rotTrn(self,x,y,theta):
        self.x, self.y = x,y
        
        dx,dy = self.r*np.cos(self.dt),self.r*np.sin(self.dt)
        self.pts = [[dx, dy],[dx,-dy],[self.tip*self.r,0]]
        for p in self.pts:
            l = np.sqrt(p[0]*p[0] + p[1]*p[1])
            alf = atan2(p[1],p[0])
            p[0] = l*np.cos(self.theta0 + theta + alf) + x
            p[1] = l*np.sin(self.theta0 + theta + alf) + y
#             print(p)
#         for p in self.pts:
#             print(p)
        return self
            
    def showAndHold(self):
        plt.ioff()
        plt.show()

    def cla(self): 
        self.ax.cla()
        return self

    def pause(self, dt):
        plt.pause(dt)
        return self

    def setLim(self,xMin=0, yMin = 0, xMax = 6, yMax = 6):
        plt.xlim(xMin,xMax)
        plt.ylim(yMin,yMax)
        self.ax.set_aspect(1)
        return self

    def text(self,x,y,str):
        
        font = {'family': 'serif',
                'color':  'darkred',
                'weight': 'normal',
                'size': 20,
                }

        self.ax.text(x,y,str,fontdict=font)
        return self

    def plot_lines(self,lines):
        for ln in lines:
            ln.plot(plt)

    def draw(self):
        patches = []
        patches.append(Circle((self.x,self.y), self.r, color='b'))
        patches.append(Polygon(self.pts,True))
       

        p = PatchCollection(patches, alpha=0.4)
        self.ax.add_collection(p)
        self.ax.grid()

        plt.pause(.001)
        return self

def test0():
    TagPozyx(tip=2).rotTrn(1,2,pi/6).draw().show()

def test1():

    tag = TagPozyx(r=0.5,tip=2).preShow()
    n = 5
    x = [0.25*i for i in range(n)]
    y = [0.5*i for i in range(n)]
    t = [0.1*i*pi for i in range(n)]
    for x,y,t in zip(x,y,t):
        tag.ax.cla()
        tag.rotTrn(x,y,t).setLim().draw()
        plt.pause(.1)  # have to have pause to allow time to draw
        # plt.pause(1.001)  # have to have pause to allow time to draw
    tag.showAndHold()

if __name__ == "__main__":    
    test1()