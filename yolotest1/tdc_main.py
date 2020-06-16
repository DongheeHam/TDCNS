import numpy as np
import argparse
import cv2 as cv
import subprocess
import time
import os
from utils import parse

if __name__ == '__main__':
	FLAGS = parse()

	# 라벨 가져오기
	labels = open(FLAGS.labels).read().strip().split('\n')

	# 라벨 색상 랜덤 초기화
	colors = np.random.randint(0, 255, size=(len(labels), 3), dtype='uint8')

	# 사전 학습된 yolov3모델을 형성하기 위한 weight, cfg 파일 로드
	net = cv.dnn.readNetFromDarknet(FLAGS.config, FLAGS.weights)
	net.setPreferableTarget(cv.dnn.DNN_TARGET_OPENCL)

	# 모델의 출력 계층 이름 가져오기
	layer_names = net.getLayerNames()
	layer_names = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
	# net 안에서 무슨일이 일어나는지 모르겠지만 layer_namse는 이렇게 생겼음 ['yolo_82', 'yolo_94', 'yolo_106']


