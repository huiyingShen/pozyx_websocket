from webSocketServerClient import getServer,getClient
from client_new import PozClient

from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout,QPushButton
from PyQt5.QtGui import QPixmap
import sys
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import numpy as np
from time import time,sleep
import threading

# adapted from https://gist.github.com/docPhil99/ca4da12c9d6f29b9cea137b617c7b8b1

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self, receiver):
        super().__init__()
        self._run_flag = True
        self.receiver = receiver
 

    def run(self):
        # capture from web cam
        cap = None
        fn = "image00.png"
        map = cv2.imread(fn)
        pozClient = PozClient(fn)
        # cap = cv2.VideoCapture(0)
        i = 0
        while self._run_flag:
            ret = True
            if cap != None: ret, cv_img = cap.read()
            else: cv_img = map.copy()

                
            if ret:
                txt = self.receiver.recv().split()
                # print(txt)
                if len(txt) == 6:
                    print(txt[2],txt[3],txt[4])
                    try:
                        # print(float(txt[2]))
                        # print(float(txt[3]))
                        # print(float(txt[4]))
                        # txt = txt[2] +', ' + txt[3]
                        xf = float(txt[2])*100 + 300
                        yf = 300 - float(txt[3])*100
            
                        theta = -float(txt[4])
                        i += 1
                        cv_img = pozClient.oneStep(xf,yf,theta,i)
                    except: 
                        pass
                else:
                    txt = 'hello!'
                    thickness=2
                    size=2
                    cv2.putText(cv_img, txt, (25,100), cv2.FONT_HERSHEY_SIMPLEX, size, (0,0,255), thickness)
                self.change_pixmap_signal.emit(cv_img)
        # shut down capture system
        if cap != None: cap.release()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()


class App(QWidget):
    def __init__(self, port=8001, launchSender = False):
        super().__init__()
            
        def sending(ws):
            while True:
                ws.send(f"time = {time()}")
                # print("sending...")
                sleep(0.1)

        server = getServer(port=port)
        self.receiver = getClient(port=port)
        if launchSender:
            sender = getClient(port=port)
            threading.Thread(target=sending, args=(sender,)).start()

        self.setWindowTitle("Qt live label demo")
        # self.disply_width = 640
        # self.display_height = 480 
        self.disply_width = 600
        self.display_height = 600
        # create the label that holds the image
        self.image_label = QLabel(self)
        self.image_label.resize(self.disply_width, self.display_height)
        # create a text label
        self.textLabel = QLabel('Webcam')
        self.btnStart = QPushButton('Send START ', self)
        self.btnStop = QPushButton('Send STOP ', self)


        # create a vertical box layout and add the two labels
        vbox = QVBoxLayout()
        vbox.addWidget(self.image_label)
        vbox.addWidget(self.btnStart)
        vbox.addWidget(self.btnStop)
        vbox.addWidget(self.textLabel)
        # set the vbox layout as the widgets layout
        self.setLayout(vbox)

        self.btnStart.clicked.connect(self.onStart)
        self.btnStop.clicked.connect(self.onStop)

        # create the video capture thread
        self.thread = VideoThread(self.receiver)
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.thread.start()

    @pyqtSlot()
    def onStart(self):
        print('Sending START,...')
        self.receiver.send("START")    
    @pyqtSlot()
    def onStop(self):
        print('Sending STOP,...')
        self.receiver.send("STOP")

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()



    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)
    
    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
    
if __name__=="__main__":
    app = QApplication(sys.argv)
    a = App(launchSender = True)
    a.show()
    sys.exit(app.exec_())

