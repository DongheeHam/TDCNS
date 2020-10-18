import numpy as np
import argparse
import cv2 as cv
import subprocess
import time
import os
from utils import parse
from configure import getSizecut, getArea
from detector import Detector
from data_processing import DataProcessing

#webstreaming
from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template
import threading
import argparse
import time
import cv2

outputFrame=None
lock = threading.Lock()
app = Flask(__name__)

def detecting(FLAGS):
	global outputFrame

	# 라벨 가져오기
	labels = open(FLAGS.labels).read().strip().split('\n')

	# 사전 학습된 yolov3모델을 형성하기 위한 weight, cfg 파일 로드
	net = cv.dnn.readNetFromDarknet(FLAGS.config, FLAGS.weights)
	# net.setPreferableTarget(cv.dnn.DNN_TARGET_OPENCL)

	net.setPreferableBackend(cv.dnn.DNN_BACKEND_CUDA)
	net.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA)
	# 모델의 출력 계층 이름 가져오기
	layer_names = net.getLayerNames()
	layer_names = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
	# net 안에서 무슨일이 일어나는지 모르겠지만 layer_namse는 이렇게 생겼음 ['yolo_82', 'yolo_94', 'yolo_106']

	# road 정보 불러오기
	"""관리 서버에서 불러오는 부분이고
    dtc는 전체 인식범위에 해당하는 한개의 다각형 2차원 배열 ex)[[x,y], [x,y], [x,y], [x,y]]
    ldtc는 각 차선별 다각형 2차원배열이 차선 개수만큼 있음 즉 3차원 배열
    용도는 각 차선을 정의해 해당 차선 안에 차가 있는지 판단하고 대기열에 추가함
    ex) [ [[x,y], [x,y], [x,y], [x,y]], [[x,y], [x,y], [x,y], [x,y]], [[x,y], [x,y], [x,y], [x,y]]]
    counter도 각 차선별로 다각형이 있음 3차원배열
    용도는 해당 counter을 통과할 때 통행량 카운팅을 함.
    """
	dtc, ldtcs, counter = getArea(FLAGS.road_number)

	# 대형차와 소형차를 구분할 크기를 정의함. box의 height가 sizecut보다 크면 대형, 작으면 소형차로 분류함.
	# 현재는 임시로 하드코딩한 값을 쓰지만 차후 서버에 저장해 가져오거나 bus truck별로 구별하거나
	# 모듈이 스스로 판단도록 해야함
	sizecut = getSizecut()

	try:
		# -st 또는 -v 에서 받아온 영상정보를 가져와 vid에 저장
		if FLAGS.video_path:
			vid = cv.VideoCapture(FLAGS.path + FLAGS.video_path)
		elif FLAGS.stream_path:
			vid = cv.VideoCapture(FLAGS.stream_path)
	except:
		raise Exception('Video cannot be loaded! Please check the path provided!')

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
	dataProcessing = DataProcessing(detector=detector,  # detector을 통채로 멤버로 둠.
									road_number=FLAGS.road_number)  # 진입로번호 (발표할때 파일저장용도로 쓰였고 큰의미 없음)

	# 카운팅 집계를 시작함
	dataProcessing.start_counting()

	frame_index = 0
	count = 0
	height, width = None, None
	while True:
		# 여기서 반복문을 돌면서 프레임별로 연산함
		# vid.read()는 영상에서 프레임 하나를 가져오고 frame에 이미지가 저장됨.
		# grabbed는 다음 프레임이 있는지 boolean
		grabbed, frame = vid.read()

		# 비디오일 경우를 대비해 비디오 종료 체크
		# 비디오가 끝나거나 프레임이 없으면 grabbed가 false를 반환함
		if not grabbed:
			# 카운트 텍스트 출력
			# 영상이 종료되면 총 카운팅된수를 print하고 종료
			car_in_lane_text_ = ""
			for i, lane in enumerate(detector.lane_count):
				car_in_lane_text_ += f"lane {i + 1} : {len(detector.lane_count[i])} | "
			print("car_in_lane_text_ : ", car_in_lane_text_);
			time.sleep(10)
			continue

		# width, height를 재설정하는거같은데 왜그랬지?
		if width is None or height is None:
			height, width = frame.shape[:2]
			detector.setHeightAndWidth(height, width)

		# cpu로 실행하면 속도 보장이 안되서
		# infer_cycle 프레임당 1번씩 객체인식하게끔 함
		# infer=False가 들어가면 객체인식은 하지 않고 전 프레임의 정보(box,count등)를 반환함
		if count == 0:
			frame = detector.infer_image(frame)
			count += 1
		else:
			frame = detector.infer_image(frame, infer=False)
			count = (count + 1) % FLAGS.infer_cycle

		# print(detector.last_car_in_lane)

		# 데이터 가공

		# queue_avg = dataProcessing.getQueueAvg(detector.last_car_in_lane)
		# dataProcessing.interval(FLAGS.interval_time)

		# 화면 출력
		# detector.show(frame)

		frame = detector.drowLines(frame)
		#cv.imshow('video', frame)
		outputFrame = frame.copy()

		if cv.waitKey(1) & 0xFF == ord('q'):
			break
		frame_index += 1

	vid.release()
def generate():
    # grab global references to the output frame and lock variables
    global outputFrame, lock
    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if outputFrame is None:
                continue
            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
            # ensure the frame was successfully encoded
            if not flag:
                continue
        # yield the output frame in the byte format
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
            bytearray(encodedImage) + b'\r\n')

@app.route("/")
def index():
    # return the rendered template
    return render_template("index.html")
@app.route("/tdcns_monitor")
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")
if __name__ == '__main__':
	FLAGS = parse()
	t = threading.Thread(target=detecting,args=(FLAGS,))
	t.daemon = True
	t.start()

	app.run(host=FLAGS.host, port=FLAGS.port, debug=True, threaded=True, use_reloader=False)
	#detecting()
