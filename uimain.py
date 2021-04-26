from multiprocessing import Process, Pipe
from time import sleep
import numpy as np
import tkinter
from PIL import Image, ImageTk

class Dummy:
    def __init__(self):
        self.x,self.y = 100.1,200.2
        self.theta = 0.0

    def one_step(self):
        sleep(0.01)
        self.x += np.random.random() - 0.3
        self.y += np.random.random() - 0.2
        self.theta += np.random.random()*np.pi
        self.theta = self.theta%(np.pi*2)


class UiCanvasApp:
    def __init__(self,im_fn = "image0.png"):
        self.root = tkinter.Tk()
        self.get_image(im_fn)
        self.set_gui()
        self.canvas.create_image(0,0, anchor=tkinter.NW, image=self.img_tk)

        self.recv_conn, self.send_conn = Pipe()
        self.dummy = Dummy()

    def target_f(self):
        for _ in range(100):
            self.dummy.one_step()
            self.send_conn.send((self.dummy.x,self.dummy.y,self.dummy.theta))
        self.send_conn.send((-1,-1,0))
        self.send_conn.close()


    def consumer(self):
        from PIL import Image, ImageTk
        x0,y0,theta0 = self.recv_conn.recv()
        r = 10
        d = 2*r
        cnt = 0
        while True:
            # try:
                x,y,theta = self.recv_conn.recv()
                if x == -1 and y == -1:
                    break
                print("x: {:6.2f}, y: {:6.2f}, theta: {:6.2f}".format(x,y,theta))
                x1,y1 = int(x0 - d), int(y0 - d)
                x2,y2 = int(x0 + d), int(y0 + d)
                # im = self.rgb[x1:x2,y1:y2,:]
                # print("im.shape = ", im.shape)
                im = self.crop_img(x1,y1,x2,y2)
                self.canvas.create_image(x1,y1, anchor=tkinter.NW, image=im)
                cnt = cnt%5
                if cnt==0: self.canvas.create_image(0,0, anchor=tkinter.NW, image=self.img_tk)
                self.paint_circle(x,y,r=r)
                self.canvas.update()
                x0,y0,theta0 = x,y,theta 
            # except: pass

    def go(self):
        p1 = Process(target=self.target_f)
        p1.start()
        self.consumer()
        p1.join() 

    def crop_img(self,x1,y1,x2,y2):
        im = self.rgb[x1:x2,y1:y2,:]
        return ImageTk.PhotoImage(image=Image.fromarray(im))

    def get_image(self,im_fn):
        import cv2
        from PIL import Image, ImageTk

        self.img_cv = cv2.imread(im_fn)
        b,g,r = cv2.split(self.img_cv)
        self.rgb = cv2.merge((r,g,b))
        print(self.rgb.shape)
        im = Image.fromarray(self.rgb)
        self.img_tk = ImageTk.PhotoImage(image=im) #tkinter.Tk() needs to be involked before this

    def set_gui(self):
        self.frame_top = tkinter.Frame(self.root)
        self.frame_top.pack()
        self.frame_bot = tkinter.Frame(self.root)
        self.frame_bot.pack(side = tkinter.BOTTOM)


        self.btn_go = tkinter.Button(self.frame_top, text="Go", fg="red",command = self.go)
        self.btn_go.pack( side = tkinter.LEFT)
        greenbutton = tkinter.Button(self.frame_top, text="Brown", fg="brown",command = lambda a=3, b=4 : print("a*b = {}".format(a*b)))
        greenbutton.pack( side = tkinter.LEFT )

        self.canvas = tkinter.Canvas(self.frame_bot,width = 600,height = 600,background = "blue")

        self.canvas.pack()

    def paint_circle(self,x,y,r=5,color = "#476042"):
        x1, y1 = x - r, y - r
        x2, y2 = x + r, y + r 
        self.canvas.create_oval( x1, y1, x2, y2, fill = color )


    def test0(self):
        # from math import sin,pi
        # x,y = 50,50
        # dx = 0.05*pi
        # for i in range(500):
        #     x += dx
        #     y += sin(i*dx)*2
        #     self.paint_circle(x,y,r=5)
        tkinter.mainloop()


# class UiMain:
#     def __init__(self):
#         self.recv_conn, self.send_conn = Pipe()
#         self.dummy = Dummy()
#         self.ui_canvas = UiCanvasApp(im_fn = "image0.png")

#     def target_f(self):
#         for _ in range(100):
#             self.dummy.one_step()
#             self.send_conn.send((self.dummy.x,self.dummy.y))
#         self.send_conn.send((-1,-1))
 
#         self.send_conn.close()

#     def consumer(self):
#         while True:
#             x,y = self.recv_conn.recv()
#             print('received ---  x: {}, y:{}'.format(x,y))
#             if x == -1 and y == -1:
#                 break

#     def go(self):
#         p1 = Process(target=self.target_f)
#         p2 = Process(target=self.consumer)
#         p1.start()
#         p2.start()
#         p1.join() 
#         p2.join()

# def test0():
#     UiMain().go()

if __name__ == '__main__':
    # test0()
    UiCanvasApp().test0()

