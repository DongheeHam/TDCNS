import json
import numpy as np
import cv2 as cv

import pandas as pd

def getUrl(name):
    with open('env_config/cctv.json', encoding='UTF8') as json_file:
        data = json.load(json_file)
    return data[name]

def getDtc(name, height, width): # 교차로에서 인식할 부분 다각형 형테의 ndarray (나중엔 서버로 받아올 정보이나 임시로 이렇게 함)
    if name=="전농":
        return np.array([[450, height], [450, 170], [650, 180], [900, height]], np.int32)
    elif name=="Sample1.avi" or name=="Sample2.avi" or name=="Sample3.avi":
        return np.array([[90, 350], [140, 160], [360, 35], [520, 35], [700, 160], [width, 350]], np.int32)
    else:
        return np.array([])
def getLdtc(name):
    if name=="Sample1.avi" or name=="Sample2.avi" or name=="Sample3.avi":
        result=[]
        result.append(np.array( [[783, 253], [680, 163], [612, 155], [683, 255]] ))
        result.append(np.array([[581, 255], [531, 106], [558, 113], [615, 161], [682, 257]]))
        result.append(np.array([[476, 257], [483, 54], [507, 54], [582, 257]]))
        result.append(np.array([[371, 258], [454, 62], [483, 62], [478, 253]]))
        result.append(np.array( [[268, 262], [428, 60], [456, 62], [446, 86], [373, 253]] ))
        result.append(np.array( [[167, 264], [391, 58], [426, 62], [270, 257]] ))
        result.append(np.array( [[66, 293], [16, 284], [18, 244], [211, 141], [257, 137], [330, 67], [378, 67], [281, 163], [158, 225], [69, 291]] ))
        return result
    else:
        return np.array([])


def getMainFrame(name, frame, height, width):
    # create a zero array
    stencil = np.zeros_like(frame[:, :, 0])
    # 다각형 좌표 지정
    polygon = getDtc(name, height, width)
    print(polygon)
    # 다각형 채우기
    cv.fillConvexPoly(stencil, polygon, 1)
    # 합치기
    img = cv.bitwise_and(frame, frame, mask=stencil)

    return img
