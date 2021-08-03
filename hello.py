import sys

from PyQt5.QtWidgets import (QApplication, QMainWindow, QMenu, QVBoxLayout, 
QSizePolicy, QMessageBox, QWidget, QPushButton)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import random
import cv2

class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.left = 10
        self.top = 10
        self.title = 'PyQt5 matplotlib example - pythonspot.com'
        self.width = 640
        self.height = 400
        self.initUI()
        

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.canvas = PlotCanvas(self, width=5, height=4)
        self.canvas.move(0,0)

        button = QPushButton('PyQt5 button', self)
        button.setToolTip('This s an example button')
        button.move(500,0)
        button.resize(140,100)


        button.clicked.connect(self.on_click)
        
        self.show()

    @pyqtSlot()
    def on_click(self):
        print('PyQt5 button click')
        
        self.canvas.nextFrame()

class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.ax = self.figure.add_subplot(111)
        self.plot()
        self.cap = cv2.VideoCapture(0)
        _,bgr = self.cap.read()
        rgb = cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
        # im = cv2.imread("image00.png")
        self.fr = self.ax.imshow(rgb)

    def nextFrame(self):
        _,bgr = self.cap.read()
        rgb = cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
        self.ax.imshow(rgb)


    def plot(self):
        data = [random.random() for i in range(25)]
        self.ax.plot(data, 'r-')
        self.ax.set_title('PyQt Matplotlib Example')
        self.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
