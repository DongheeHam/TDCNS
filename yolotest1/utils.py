import json
import numpy as np
import cv2 as cv

import pandas as pd

def getUrl(name):
    with open('cctv.json', encoding='UTF8') as json_file:
        data = json.load(json_file)
    return data[name]

def getPolygon(name, height, width):
    if name=="전농":
        return np.array([[450, height], [450, 170], [650, 180], [900, height]])
    elif name=="Sample1.avi" or name=="Sample2.avi" or name=="Sample3.avi":
        return np.array([[90, 370], [140, 160], [360, 35], [520, 35], [700, 160], [width, 90]])


def getMainFrame(name, frame, height, width):
    # create a zero array
    stencil = np.zeros_like(frame[:, :, 0])
    # 다각형 좌표 지정
    polygon = getPolygon(name, height, width)
    print(polygon)
    # 다각형 채우기
    cv.fillConvexPoly(stencil, polygon, 1)
    # 합치기
    img = cv.bitwise_and(frame, frame, mask=stencil)

    return img
