import json
import numpy as np
import cv2 as cv

import pandas as pd

def getUrl(name):
    with open('cctv.json') as json_file:
        data = json.load(json_file)
    return data[name]

def getPoligon(name, height, width):
    if name=="전농":
        return np.array([[450, height], [450, 170], [650, 180], [900, height]])

def getMainFrame(name, frame, height, width):
    # create a zero array
    stencil = np.zeros_like(frame[:, :, 0])
    # 다각형 좌표 지정
    polygon = getPoligon(name, height, width)
    # 다각형 채우기
    cv.fillConvexPoly(stencil, polygon, 1)
    # 합치기
    img = cv.bitwise_and(frame, frame, mask=stencil)

    return img
