from flask import Flask,render_template,request,jsonify
import cv2
import numpy as np
import os,time

class Pnt:
    def __init__(self,x=0,y=0,z=0):
        self.x,self.y,self.z = int(x),int(y), int(z)
        self.isNew = False
pnt = Pnt()

app = Flask(__name__, template_folder='templates')

x,y = 0,0
@app.route("/")
def hello():
    return render_template('index.html')

@app.route('/xyz', methods=['GET', 'POST'])
def pozyx_xyz():
    if request.method == 'POST':
        request.get_data()
        pnt.x = int(request.form.get('x'))
        pnt.y = int(request.form.get('y'))
        pnt.z = int(request.form.get('z'))
        pnt.isNew = True

        return jsonify("got xyz")
    if request.method == 'GET': 
        r = {'x':pnt.x, 'y':pnt.y, 'z':pnt.z, 'isNew':pnt.isNew}
        if pnt.isNew: pnt.isNew = False
        print(r)
        return r


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug = True)