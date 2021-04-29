from multiprocessing import Process, Pipe
from time import sleep
import numpy as np
import tkinter
from tkinter import Tk,Frame,Button,Label,Entry,Radiobutton,IntVar,END,StringVar
import sound_plot
import localize_new

from sound_plot import PozyxParam

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
        fLowEntry.place(x=x1, y=y, width = width)
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

class Status:
    def __init__(self):
        self.done = False

class Driver:

    def __init__(self):
        self.root = Tk()
        window = Frame(self.root,width=320,height=400)
        window.pack()

        self.status = Status()

        self.t = Trial(window, y = 0)  
        self.p = Param_GUI(window, y = 80)

        self.vTxt = StringVar()
        self.timer = Label(window, textvariable=self.vTxt, fg='blue',font=("Helvetica", 24))
        self.vTxt.set("%02i:%02i" % (self.t.min, 0))
        self.timer.place(x=110,y=250)

        self.window = window

 
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
        while sec >0 and not self.status.done:
            sleep(1)
            dt = time() - t0
            sec = int(sec0 - dt)
            mm = int(sec/60)
            ss = sec - mm*60
            self.vTxt.set("%02i:%02i" % (mm, ss))
            self.timer.update()

        self.status.done = True  # time runs out

    def start(self):
        import threading
        threading.Thread(target=self.start1).start()


    def stop(self):
        print("stop")
        self.status.done = True

    def go(self):
        Button(self.window, text="Start", fg='green', command=self.start).place(x=70, y=300)    
        Button(self.window, text="Stop", fg='red', command=self.stop).place(x=200, y=300)

        self.root.title('Pozyx Trial')
        self.root.mainloop()

class Dummy:
    def __init__(self):
        self.x,self.y = 100.1,200.2
        self.theta = 0.0

    def one_step(self):
        sleep(0.01)
        self.x += np.random.random()*10 - 3
        self.y += np.random.random()*10 - 2
        self.theta += np.random.random()*10
        self.theta = self.theta%360
 
def target(send_conn):
    # dummy = Dummy()
    # for _ in range(100):
    #     dummy.one_step()
    #     send_conn.send((dummy.x,dummy.y,dummy.theta))
    localize_new.main(send_conn)
    send_conn.send((-1,-1,0))
    send_conn.close()

class Controller:
    def __init__(self):
        self.root = tkinter.Tk()
        self.set_gui()
        self.recv_conn, self.send_conn = Pipe()
        self.dummy = Dummy()

    def target_f(self):
        for _ in range(100):
            self.dummy.one_step()
            self.send_conn.send((self.dummy.x,self.dummy.y,self.dummy.theta))
        self.send_conn.send((-1,-1,0))
        self.send_conn.close()

    def flip(self):
        pass

    def consumer(self):
        r = 10
        while True:
            try:
                x,y,theta = self.recv_conn.recv()
                if x == -1 and y == -1:
                    break
                print("x: {:6.2f}, y: {:6.2f}, theta: {:6.2f}".format(x,y,theta))
            except: pass

    def go(self):
        # p1 = Process(target=self.target_f)
        p1 = Process(target=target, args=(self.send_conn,))
        p1.start()
        sound_plot.main(self.recv_conn,fn_im="image0.png")
        p1.join() 

    def set_gui(self):
        self.frame_top = tkinter.Frame(self.root)
        self.frame_top.pack()
        self.frame_bot = tkinter.Frame(self.root)
        self.frame_bot.pack(side = tkinter.BOTTOM)


        self.btn_go = tkinter.Button(self.frame_top, text="Go", fg="red",command = self.go)
        self.btn_go.pack( side = tkinter.LEFT)
        greenbutton = tkinter.Button(self.frame_top, text="Brown", fg="brown",command = lambda a=3, b=4 : print("a*b = {}".format(a*b)))
        greenbutton.pack( side = tkinter.LEFT )

        self.btn_flip = tkinter.Button(self.frame_bot, text="Flip", fg="red",command = self.flip)
        self.btn_flip.pack( side = tkinter.LEFT)


    def test0(self):
        tkinter.mainloop()
if __name__ ==  "__main__":
    # Controller().test0()
    # Param_GUI().test0()
    # Trial(Tk()).test0()
    Driver().go()