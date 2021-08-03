from time import sleep
import numpy as np
import tkinter
from tkinter import Tk,Frame,Button,Label,Entry,Radiobutton,IntVar,END,StringVar
import sound_plot

# from simple_websocket_server import WebSocketServer, WebSocket
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import threading
from time import sleep

from client_new import PozClient

started = False
clients = []
# pozClient = PozClient().test0()
class SimpleChat(WebSocket):
    i = 0

    def handleMessage(self):
        for client in clients:
            if client != self:
                client.sendMessage(self.address[0] + u' - ' + self.data)
                # print(self.data)
                # out = self.data.split(' ')
                # print(out)
                # try:
                #     x = float(out[0])*100
                #     y = float(out[1])*100
                #     theta = float(out[2])
                #     ix = int(x) + 300
                #     iy = int(y) + 300
                #     self.i += 1
                #     # self.pozClient.oneStep(ix,iy,theta,self.i)
                # except:
                #     print("error parsing x,y,theta")

    def handleConnected(self):
        print(self.address, 'connected')
        for client in clients:
            client.sendMessage(self.address[0] + u' - connected')
        clients.append(self)

    def handleClose(self):
       clients.remove(self)
       print(self.address, 'closed')
       for client in clients:
          client.sendMessage(self.address[0] + u' - disconnected')


# import websocket
# class MyWebSocket(websocket.WebSocket):


class Trial:
    def __init__(self, window, y=0):
   
        self.subjName = "Doe"
        self.min = 30

        x1,width= 180,50 
        self.nameEntry = Entry(window, text=self.subjName, bd=1)
        self.nameEntry.place(x=x1, y=y, width = width)
        self.nameEntry.insert(END,self.subjName)
        Label(window, text="Subj. Name:", fg='blue', font=("Helvetica", 10)).place(x=20, y=y)

        y += 30
        self.minE = Entry(window, bd=1)
        self.minE.place(x=x1, y=y, width = width)
        self.minE.insert(END, str(self.min))
        Label(window, text="Trial Duration (min)", fg='blue', font=("Helvetica", 10)).place(x=20, y=y)

    def get_val(self):
        self.subjName = self.nameEntry.get()
        self.min = int(self.minE.get())
        print("self.subjName  = {}".format(self.subjName) )
        print("self.min  = {}".format(self.min) )

class PozyxParam:
    def __init__(self):
        self.isExp = True
        self.isHigh2Low = True
        self.freqLow = 300.0
        self.freqHigh = 1000.0
        self.distMax = 600.0  
        self.alpha = 0.5

    def getFreq(self, d):
        f1 = self.freqLow
        f2 = self.freqHigh
        if self.isHigh2Low:
            f1,f2 = f2,f1

        coef = 2.0  # quick fix by Christopher 
        if self.isExp: return self.freq_exp(d, f1, f2)*coef
        else: return self.freq_linear(d,f1, f2)*coef

    def getScaledD(self,d):
        print("getScaledD, alpha = ",self.alpha)
        return pow(d/self.distMax,self.alpha)
    
    def  freq_linear(self,d, f_min, f_max):
        return f_min + (f_max-f_min)*self.getScaledD(d)
    

    def freq_exp(self,d, f_min, f_max):
        return f_min*pow(f_max/f_min,self.getScaledD(d))        
        
class Param_GUI(PozyxParam):
    def __init__(self, window, y = 0):
        super().__init__()

        x1,x2 = 120,220
        f_type=IntVar()
        f_type.set(1)
        Radiobutton(window, text="Exp.", variable=f_type,value=1).place(x=x1,y=y)
        Radiobutton(window, text="Linear", variable=f_type,value=2).place(x=x2, y=y)
        Label(window, text="Function Type:", fg='blue', font=("Helvetica", 10)).place(x=20, y=y)
        self.f_type = f_type

        y += 30
        f_direction=IntVar()
        f_direction.set(1)
        Radiobutton(window, text="High to Low", variable=f_direction,value=1).place(x=x1,y=y)
        Radiobutton(window, text="Low to High", variable=f_direction,value=2).place(x=x2, y=y)
        Label(window, text="Freq. Direction:", fg='blue', font=("Helvetica", 10)).place(x=20, y=y)
        self.f_direction = f_direction

        y += 30; x1 = 100; width = 80
        fLowEntry = Entry(window,bd = 2, width = 80)
        fLowEntry.place(x=x1,  y=y, width = width)
        fLowEntry.insert(END, str(int(self.freqLow)))
        Label(window,text = "fregLow", fg='blue').place(x=20, y=y)

        y += 30
        fHighEntry = Entry(window,bd = 2)
        fHighEntry.place(x=x1, y=y, width = width)
        fHighEntry.insert(END, str(int(self.freqHigh)))
        Label(window,text = "freqHigh", fg='blue').place(x=20, y=y)

        y += 30
        alphaEntry = Entry(window,bd = 2)
        alphaEntry.place(x=x1, y=y, width = width)
        alphaEntry.insert(END, "{:5.2f}".format(self.alpha))
        Label(window,text = "alpha", fg='blue').place(x=20, y=y)

        # y += 50
        # btn=Button(window, text="Set Value", fg='green', command=self.get_param)
        # btn.place(x=80, y=y)

        self.fLowEntry = fLowEntry
        self.fHighEntry = fHighEntry
        self.alphaEntry = alphaEntry


    def get_param(self):
        self.isExp = self.f_type.get() == 1
        self.isHigh2Low = self.f_direction.get() == 1
        self.freqLow = float(self.fLowEntry.get())
        self.freqHigh = float(self.fHighEntry.get())
        self.alpha = float(self.alphaEntry.get())
        print("self.isExp  = {}".format(self.isExp) )
        print("self.isHigh2Low  = {}".format(self.isHigh2Low) )
        print("self.freqLow  = {}".format(self.freqLow) )
        print("self.freqHigh  = {}".format(self.freqHigh) ) 
        print("self.alpha  = {}".format(self.alpha) )
        # print("go!")


class Driver:

    def __init__(self):

        self.pozClient = PozClient()
        self.root = Tk()
        window = Frame(self.root,width=320,height=400)
        window.pack()

        self.t = Trial(window, y = 0)  
        self.p = Param_GUI(window, y = 80)

        self.vTxt = StringVar()
        self.timer = Label(window, textvariable=self.vTxt, fg='blue',font=("Helvetica", 24))
        self.vTxt.set("%02i:%02i" % (self.t.min, 0))
        self.timer.place(x=110,y=250)

        self.window = window

        self.fn = "doe.txt"
        self.done = False

        port = "8001"
        server = SimpleWebSocketServer('', int(port), SimpleChat)
        threading.Thread(target=server.serveforever).start()

        import websocket
        self.ws = websocket.WebSocket()
        self.ws.connect("ws://localhost:"+port, origin="local")
        self.i = 0
 
    def getMsg(self):
        while self.done is False:
            txt = self.ws.recv()
            print("txt = ", txt)
            out = txt.split(' ')[2:]
            print(out)
            try:
                x = float(out[0])*100
                y = float(out[1])*100
                theta = float(out[2])
                ix = int(x) + 300
                iy = int(y) + 300
                self.i += 1
                # self.pozClient.oneStep(ix,iy,theta,self.i)
            except:
                print("error parsing x,y,theta")
            

    def start1(self):
        import time as time0
        from time import time,sleep
        t0 = time()
        self.t.get_val()
        self.p.get_param()

        # print(time0.strftime('%Y-%m-%d-%H-%M', time0.gmtime(t0)))

        self.fn = self.t.subjName +'-'+ time0.strftime('%Y-%m-%d-%H-%M', time0.gmtime(t0))+'.txt'
        Label(self.window, text="Data File: "+self.fn, fg='blue',font=("Helvetica", 10)).place(x=50,y=330)
        sec0 = self.t.min*60
        sec = sec0
        while sec >0 and not self.done:
            sleep(1)
            dt = time() - t0
            sec = int(sec0 - dt)
            mm = int(sec/60)
            ss = sec - mm*60
            self.vTxt.set("%02i:%02i" % (mm, ss))
            print("%02i:%02i" % (mm, ss))
            self.timer.update()

        self.done = True  # time runs out

    def start(self):
        print("start")
        self.ws.send("Start")
        import threading
        threading.Thread(target=self.start1).start()
        threading.Thread(target=self.getMsg).start()
        

    def stop(self):
        print("stop")
        self.ws.send("End")
        self.done = True

    def go(self, start, stop):
        Button(self.window, text="Start", fg='green', command=start).place(x=70, y=300)    
        Button(self.window, text="Stop", fg='red', command=stop).place(x=200, y=300)

        self.root.title('Pozyx Trial')
        self.root.mainloop()

    def test0(self):
        self.go(self.start,self.stop)

if __name__ ==  "__main__":
    Driver().test0()