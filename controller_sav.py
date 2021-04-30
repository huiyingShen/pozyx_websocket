from multiprocessing import Process, Pipe
from time import sleep
import numpy as np
import tkinter
from tkinter import Tk,Frame,Button,Label,Entry,Radiobutton,IntVar,END,StringVar
import sound_plot
import localize_new

from sound_plot import PozyxParam

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