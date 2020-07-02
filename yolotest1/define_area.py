import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, RadioButtons
from matplotlib.collections import LineCollection

import cv2 as cv
import argparse
import copy
import requests

import json

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file',
                    type=str)
parser.add_argument('-p', '--path',
                    type=str,
                    default='./picture/')
parser.add_argument('-st', '--stream',
                    type=str)
parser.add_argument('-r', '--road-number',
                    type=int)
FLAGS, unparsed = parser.parse_known_args()
if FLAGS.file:
    cap = cv.VideoCapture(FLAGS.path + FLAGS.file)
elif FLAGS.stream:
    cap = cv.VideoCapture(FLAGS.stream)
ret, image = cap.read()

fig, ax = plt.subplots()
plt.subplots_adjust(left=0.25, bottom=0.25)

axcolor = 'aliceblue'

rax = plt.axes([0.025, 0.5, 0.15, 0.15])
radio = RadioButtons(rax, ('dtc', 'ldtc', 'counter'), active=0)

resetax = plt.axes([0.8, 0.025, 0.1, 0.04])  # 리셋버튼 영역
button = Button(resetax, 'send', color=axcolor, hovercolor='0.5')

type="dtc"
def reset(event):
    global lines
    if lines[-1]==[]:
        del lines[-1]
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    if type=="dtc":
        url='http://35.224.46.11:80/rest/setDtc.json'
        data={"rno":FLAGS.road_number,"dtc":lines[0]}
    elif type=='counter':
        url = 'http://35.224.46.11:80/rest/setCounter.json'
        data={"rno":FLAGS.road_number,"counter":lines}
    else:
        url = 'http://35.224.46.11:80/rest/setLdtc.json'
        data = {"rno": FLAGS.road_number, "ldtc": lines}
    print("headers : ",headers)
    print("data : ",data)
    response = requests.post(url, headers=headers, data=json.dumps(data))
def select(event):
    global type
    type = event




button.on_clicked(reset)
radio.on_clicked(select)

line=[]
ax.imshow(image)
points = []
lcs=[]
lines=[]

def onclick(event):
    if not event.xdata or event.xdata < 1 or event.ydata < 1:
        return
    if event.button == 1:
        if len(lines)==0:
            lines.append([])
        lines[-1].append([int(event.xdata),int(event.ydata)])
        print("lines : ",lines)
        print("type : ", type)
        lc = LineCollection(lines, color="green", linewidths=1.5)
        lcs.append(lc)
        ax.add_collection(lc)
        plt.draw()

        print(lines)

        print(event.xdata, event.ydata)
        x = int(np.round(event.xdata))
        y = int(np.round(event.ydata))
        points.append([x,y])
    elif event.button==2:
        print("Result = np.array(",points,")")
        del points[:]
    elif event.button==3:
        lines[-1].append(lines[-1][0])

        lc = LineCollection(lines, color="green", linewidths=2)
        ax.add_collection(lc)
        #del lines[:]
        plt.draw()
        lines.append([])
        #print("Result = np.array(",points,")")
        del points[:]

plt.gcf().canvas.mpl_connect('button_press_event', onclick)

plt.show()

