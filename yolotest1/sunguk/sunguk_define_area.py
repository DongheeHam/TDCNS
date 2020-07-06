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
                    default='../picture/')
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

fig, ax = plt.subplots() # fig는 전체 사이즈, ax 는각각의 서브플롯
plt.subplots_adjust(left=0.25, bottom=0.25)  #cap이 그려질 그래프 위치 조정

axcolor = 'aliceblue'   # 컬러 설정

rax = plt.axes([0.025, 0.5, 0.15, 0.15])   # 좌측 라디오 버튼 박스의 위치와 크기를 지정
radio = RadioButtons(rax, ('dtc', 'ldtc', 'counter'), active=0)

resetax = plt.axes([0.8, 0.025, 0.1, 0.05])  # send 버튼 박스의 위치와 크기를 지정
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
        url = 'http://35.224.46.1 1:80/rest/setLdtc.json'
        data = {"rno": FLAGS.road_number, "ldtc": lines}
    print("headers : ",headers)
    print("data : ",data)
    response = requests.post(url, headers=headers, data=json.dumps(data))


def select(event):
    global type
    type = event

button.on_clicked(reset)   # send 버튼 클릭시 reset 함수 실행

radio.on_clicked(select)   #radio버튼 클릭시 select 함수 실행 type 변경

line=[]
ax.imshow(image)
points = []
lcs=[]
lines=[]

def onclick(event):
    if not event.xdata or event.xdata < 1 or event.ydata < 1:
        return
    if event.button == 1:   # 마우스 좌클릭시
        if len(lines)==0:
            lines.append([])
        lines[-1].append([int(event.xdata),int(event.ydata)])   # lines에 append해주고
        print("lines : ",lines)            # 출력한다
        print("type : ", type)             # 타입도
        lc = LineCollection(lines, color="green", linewidths=1.5)
        lcs.append(lc)
        ax.add_collection(lc)
        plt.draw()          # 라인그리는내용인듯

        print(lines)

        print(event.xdata, event.ydata)
        print("--------------------------------------------------------------------------")
        x = int(np.round(event.xdata))           # np.round  반올림함수
        y = int(np.round(event.ydata))
        points.append([x,y])              # points에도 x,y 값좌표를 넣어준다
    elif event.button==2:
        print("Result = np.array(",points,")")
        del points[:]
    elif event.button==3:               # 마우스 우클릭시 lines 마지막 값을
        lines[-1].append(lines[-1][0])         #lines 첫값이랑 동일하게 해준다  왜냐하면, 다각형좌표 를완성하기 위해
        lc = LineCollection(lines, color="green", linewidths=2)
        ax.add_collection(lc)
        #del lines[:]
        plt.draw()
        lines.append([])
        #print("Result = np.array(",points,")")
        del points[:]

plt.gcf().canvas.mpl_connect('button_press_event', onclick)

plt.show()

