# olotest1\sunguk>python sunguk_main.py -r 1 -l ../yolov3-coco/coco-labels -w ../yolov3-coco/yolov3.weights -cfg ../yolov3-coco/yolov3.cfg


import numpy as np
import argparse
import cv2 as cv
import subprocess
import time
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from utils import parse
from configure import getSizecut, getArea
from detector import Detector
from data_processing import DataProcessing

FLAGS = parse()
labels = open(FLAGS.labels).read().strip().split('\n')

# 사전 학습된 yolov3모델을 형성하기 위한 weight, cfg 파일 로드
net = cv.dnn.readNetFromDarknet(FLAGS.config, FLAGS.weights)
net.setPreferableTarget(cv.dnn.DNN_TARGET_OPENCL)

layer_names = net.getLayerNames()
layer_names = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]


dtc, ldtcs, counter = getArea(FLAGS.road_number)

sizecut = getSizecut()  # 120으로 지정해둠

vid = cv.VideoCapture("../picture/Sample1.avi")
#비디오 불러오기

# detector을 선언
detector = Detector(net=net,  # yolo
					layer_names=layer_names,  # yolo
					FLAGS=FLAGS,  # 설정 정보
					dtc=dtc,  # 인식할 좌표
					ldtcs=ldtcs,  # 차선별 좌표
					counter=counter,  # 카운팅존 좌표
					labels=labels,  # 인식 결과 classid가 번호로 나오는데 그 classid에 매핑되는 라벨(car, bus, truck 등)
					sizecut=sizecut  # 대소형 차량 구분할 크기
					)

# print("net:",detector.net)
# print("layer_names:",detector.layer_names)
# print("FLAGS:",detector.FLAGS)
# print("ldtcs:",detector.ldtcs)
# print("counter:",detector.counter)
# print("labels:",detector.labels)
# print("sizecut:",detector.sizecut)



dataProcessing = DataProcessing(detector=detector, # detector을 통채로 멤버로 둠.
					road_number=FLAGS.road_number) # 진입로번호 (발표할때 파일저장용도로 쓰였고 큰의미 없음)

dataProcessing.start_counting()

frame_index = 0
count = 0
height, width = None, None

#print(detector.lane_count)


while True:
	grabbed, frame = vid.read()
	if not grabbed:
		car_in_lane_text_ = ""
		for i, lane in enumerate(detector.lane_count):
			car_in_lane_text_ += f"lane {i + 1} : {len(detector.lane_count[i])} | "
		print("car_in_lane_text_ : ", car_in_lane_text_);
		#car_in_lane_text_ :  lane 1 : 3 | lane 2 : 2 | lane 3 : 2 |
		#이런식으로 나옴 근데 지금 lane_count가 빈 배열이라 안나옴
		break

	if width is None or height is None:
		height, width = frame.shape[:2]
		#print(frame.shape[:2])            #그냥 높이 넓이 지정해주는거
		detector.setHeightAndWidth(height, width)

	if count == 0:
		sunguk_img = detector.getDtcFrame(frame)
		frame = detector.infer_image(frame)  #여기서 오류
		count += 1
# 	else:
# 		frame = detector.infer_image(frame, infer=False)
# 		count = (count + 1) % FLAGS.infer_cycle
#
# 	detector.show(frame)
#
# 	if cv.waitKey(1) & 0xFF == ord('q'):
# 		break
# 	frame_index += 1
#
# vid.release()
#
#
# print(cv.__version__)
