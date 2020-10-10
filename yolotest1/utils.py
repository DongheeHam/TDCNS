import json
import numpy as np
import cv2 as cv
import argparse
import pandas as pd

# def getUrl(name):
#     with open('env_config/cctv.json', encoding='UTF8') as json_file:
#         data = json.load(json_file)
#     return data[name]
#
# def getDtc(name): # 교차로에서 인식할 부분 다각형 형테의 ndarray (나중엔 서버로 받아올 정보이나 임시로 이렇게 함)
#     if name=="전농":
#         return np.array([[450, 720], [450, 170], [650, 180], [900, 720]], np.int32)
#     elif name=="Sample1.avi" or name=="Sample2.avi" or name=="Sample3.avi":
#         return np.array([[90, 350], [140, 160], [360, 35], [520, 35], [700, 160], [912, 350]], np.int32)
#     else:
#         return np.array([])
#
# def getLdtc(road_number):
#     if road_number==1:
#         result=[]
#         result.append(np.array( [[783, 253], [680, 163], [612, 155], [683, 255]] ))
#         result.append(np.array([[581, 255], [531, 106], [558, 113], [615, 161], [682, 257]]))
#         result.append(np.array([[476, 257], [483, 54], [507, 54], [582, 257]]))
#         result.append(np.array([[371, 258], [454, 62], [483, 62], [478, 253]]))
#         result.append(np.array( [[268, 262], [428, 60], [456, 62], [446, 86], [373, 253]] ))
#         result.append(np.array( [[167, 264], [391, 58], [426, 62], [270, 257]] ))
#         result.append(np.array( [[66, 293], [16, 284], [18, 244], [211, 141], [257, 137], [330, 67], [378, 67], [281, 163], [158, 225], [69, 291]] ))
#         return result
#     else:
#         return np.array([])
#
#
# def getMainFrame(name, frame, height, width):
#     # create a zero array
#     stencil = np.zeros_like(frame[:, :, 0])
#     # 다각형 좌표 지정
#     polygon = getDtc(name)
#     # 다각형 채우기
#     cv.fillConvexPoly(stencil, polygon, 1)
#     # 합치기
#     img = cv.bitwise_and(frame, frame, mask=stencil)
#
#     return img

#############################################################
def parse():
    parser = argparse.ArgumentParser()

    parser.add_argument('-m', '--model-path',
                        type=str,
                        default='./yolov3-coco/',
                        help='The directory where the model weights and \
    			  configuration files are.')

    parser.add_argument('-w', '--weights',
                        type=str,
                        default='./yolov3-coco/yolov3.weights',
                        help='Path to the file which contains the weights \
    			 	for YOLOv3.')

    parser.add_argument('-cfg', '--config',
                        type=str,
                        default='./yolov3-coco/yolov3.cfg',
                        help='Path to the configuration file for the YOLOv3 model.')

    parser.add_argument('-v', '--video-path',
                        type=str,
                        help='The path to the video file')

    parser.add_argument('-p', '--path',
                        type=str, default="./picture/")

    parser.add_argument('-st', '--stream-path',
                        type=str,
                        help='The path to the video file')

    # 객체인식은 진입로(road)별로 진행되며 road 고유번호를 필수로 입력해야 한다.
    # road 번호를 토대로 동작함.
    parser.add_argument('-r', '--road-number', type=int)

    parser.add_argument('-ic', '--infer-cycle', type=int, default=2)

    parser.add_argument('-vo', '--video-output-path',
                        type=str,
                        default='./output.avi',
                        help='The path of the output video file')

    parser.add_argument('-l', '--labels',
                        type=str,
                        default='./yolov3-coco/coco-labels',
                        help='Path to the file having the labels in a new-line seperated way.')

    parser.add_argument('-c', '--confidence',
                        type=float,
                        default=0.35,
                        help='The model will reject boundaries which has a \
    				probabiity less than the confidence value. \
    				default: 0.5')

    parser.add_argument('-th', '--threshold',
                        type=float,
                        default=0.3,
                        help='The threshold to use when applying the \
    				Non-Max Suppresion')

    parser.add_argument('-t', '--show-time',
                        type=bool,
                        default=False,
                        help='Show the time taken to infer each image.')

    parser.add_argument('-n', '--name',
                        type=str)

    FLAGS, _ = parser.parse_known_args()
    return FLAGS