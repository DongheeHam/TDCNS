import numpy as np
import argparse
import cv2 as cv
import subprocess
import time
import os
from utils import parse
from configure import getDtcArea, getLdtcsArea, getArea
from detector import Detector
from data_processing import DataProcessing

if __name__ == '__main__':
	FLAGS = parse()

	# 라벨 가져오기
	labels = open(FLAGS.labels).read().strip().split('\n')

	# 사전 학습된 yolov3모델을 형성하기 위한 weight, cfg 파일 로드
	net = cv.dnn.readNetFromDarknet(FLAGS.config, FLAGS.weights)
	net.setPreferableTarget(cv.dnn.DNN_TARGET_OPENCL)

	# 모델의 출력 계층 이름 가져오기
	layer_names = net.getLayerNames()
	layer_names = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
	# net 안에서 무슨일이 일어나는지 모르겠지만 layer_namse는 이렇게 생겼음 ['yolo_82', 'yolo_94', 'yolo_106']

	# road 정보 불러오기
	#dtc = getDtcArea(FLAGS.road_number)
	#ldtcs = getLdtcsArea(FLAGS.road_number)
	dtc, ldtcs = getArea(FLAGS.road_number)

	# opencv videoCapture

	try:
		if FLAGS.video_path:
			vid = cv.VideoCapture(FLAGS.path+FLAGS.video_path)
		elif FLAGS.stream_path:
			vid = cv.VideoCapture(FLAGS.stream_path)
	except:
		raise Exception('Video cannot be loaded! Please check the path provided!')

	detector = Detector(net=net,
						layer_names=layer_names,
						FLAGS=FLAGS,
						vid=vid,
						dtc=dtc,
						ldtcs=ldtcs,
						labels=labels
						)
	dataProcessing = DataProcessing()
	#dataProcessing.dataStatistics(FLAGS.interval_time)

	frame_index = 0
	count = 0
	height, width = None, None
	while True:
		grabbed, frame = vid.read()
		# 비디오일 경우를 대비해 비디오 종료 체크
		if not grabbed:
			break
		if width is None or height is None:
			height, width = frame.shape[:2]
			detector.setHeightAndWidth(height, width)

		# 쓸데없는 연산 방지 infer_cycle 프레임당 1번 detection
		if count == 0:
			frame = detector.infer_image(frame)
			count += 1
		else:
			frame = detector.infer_image(frame, infer=False)
			count = (count + 1) % FLAGS.infer_cycle

		print(detector.last_car_in_lane)

		# 데이터 가공

		#queue_avg = dataProcessing.getQueueAvg(detector.last_car_in_lane)
		#dataProcessing.interval(FLAGS.interval_time)

		# 화면 출력
		detector.show(frame)

		if cv.waitKey(1) & 0xFF == ord('q'):
			break
		frame_index+=1

	vid.release()
