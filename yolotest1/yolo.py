import numpy as np
import argparse
import cv2 as cv
import subprocess
import time
import os
from yolo_utils import infer_image, show_image
from utils import getUrl, getMainFrame, getDtc, getLdtc

FLAGS = []

if __name__ == '__main__':
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
						type=bool, default=True,
						help='The path to the video file')

	parser.add_argument('-st', '--stream-path',
		type=str,
		help='The path to the video file')

	# 객체인식은 진입로(road)별로 진행되며 road 고유번호를 필수로 입력해야 한다.
	# road 번호를 토대로 동작함.
	parser.add_argument('-r', '--road-number',
						type=int)

	parser.add_argument('-vo', '--video-output-path',
		type=str,
        default='./output.avi',
		help='The path of the output video file')

	parser.add_argument('-l', '--labels',
		type=str,
		default='./yolov3-coco/coco-labels',
		help='Path to the file having the \
					labels in a new-line seperated way.')

	parser.add_argument('-c', '--confidence',
		type=float,
		default=0.5,
		help='The model will reject boundaries which has a \
				probabiity less than the confidence value. \
				default: 0.5')

	parser.add_argument('-th', '--threshold',
		type=float,
		default=0.3,
		help='The threshold to use when applying the \
				Non-Max Suppresion')

	parser.add_argument('--download-model',
		type=bool,
		default=False,
		help='Set to True, if the model weights and configurations \
				are not present on your local machine.')

	parser.add_argument('-t', '--show-time',
		type=bool,
		default=False,
		help='Show the time taken to infer each image.')

	parser.add_argument('-n', '--name',
						type=str,
						default="전")

	FLAGS, unparsed = parser.parse_known_args()

	# Download the YOLOv3 models if needed
	if FLAGS.download_model:
		subprocess.call(['./yolov3-coco/get_model.sh'])

	# Get the labels
	labels = open(FLAGS.labels).read().strip().split('\n')

	# Intializing colors to represent each label uniquely
	colors = np.random.randint(0, 255, size=(len(labels), 3), dtype='uint8')

	# Load the weights and configutation to form the pretrained YOLOv3 model
	net = cv.dnn.readNetFromDarknet(FLAGS.config, FLAGS.weights)
	net.setPreferableTarget(cv.dnn.DNN_TARGET_OPENCL)

	# Get the output layer names of the model
	layer_names = net.getLayerNames()
	layer_names = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

	print(layer_names)


	if FLAGS.video_path:
		# Read the video
		try:
			if FLAGS.path:
				path = "./picture/"+FLAGS.video_path
			else:
				path = FLAGS.video_path
			vid = cv.VideoCapture(path)
			height, width = None, None
			writer = None
		except:
			raise Exception('Video cannot be loaded! Please check the path provided!')

		finally:
			while True:
				grabbed, frame = vid.read()

			    # Checking if the complete video is read
				if not grabbed:
					break
				lanes = getLdtc(FLAGS.video_path)
				if width is None or height is None:
					height, width = frame.shape[:2]
				main = getMainFrame(FLAGS.video_path, frame, height, width)
				frame, _, _, _, _ = infer_image(net, layer_names, height, width,
												main, frame, colors, labels, FLAGS, lanes=lanes)

				# dtc그리기
				area = getDtc(FLAGS.video_path, height, width)
				print("area : ",area)
				cv.polylines(frame,[area],True,(255,0,0),1)

				# ldtc그리기
				for lane in lanes:
					cv.polylines(frame, [lane], True, (0, 255, 0), 1)

				# if writer is None:
				# 	# Initialize the video writer
				# 	fourcc = cv.VideoWriter_fourcc(*"MJPG")
				# 	writer = cv.VideoWriter(FLAGS.video_output_path, fourcc, 30,
				# 		            (frame.shape[1], frame.shape[0]), True)
				#writer.write(frame)
				cv.imshow('video', frame)

				if cv.waitKey(1) & 0xFF == ord('q'):
					break

			print ("[INFO] Cleaning up...")
			#writer.release()
			vid.release()


	elif FLAGS.stream_path:

		# Infer real-time on webcam
		count = 0
		vid = cv.VideoCapture(FLAGS.stream_path)
		while True:
			_, frame = vid.read()

			height, width = frame.shape[:2]

			if count == 0:

				frame, boxes, confidences, classids, idxs = infer_image(net, layer_names, \
													height, width, frame, frame, colors, labels, FLAGS)
				count += 1

			else:
				frame, boxes, confidences, classids, idxs = infer_image(net, layer_names, \
													height, width, frame, frame, colors, labels, FLAGS,
													boxes, confidences, classids, idxs, infer=False)

				count = (count + 1) % 6

			cv.imshow('stream', frame)

			if cv.waitKey(1) & 0xFF == ord('q'):
				break

		vid.release()

		cv.destroyAllWindows()
	elif FLAGS.name:
		count = 0
		url = getUrl(FLAGS.name)
		vid = cv.VideoCapture(url)
		# _, frame = vid.read()
		# height, width = frame.shape[:2]
		# main = getMainFrame(FLAGS.name, frame, height, width)

		while True:
			_, frame = vid.read()
			height, width = frame.shape[:2]
			#main = getMainFrame(FLAGS.name, frame, height, width)
			if count == 0:
				frame, boxes, confidences, classids, idxs = infer_image(net, layer_names, \
		    						height, width, frame, frame, colors, labels, FLAGS)
				count += 1
			else:
				frame, boxes, confidences, classids, idxs = infer_image(net, layer_names, \
		    						height, width, frame, frame, colors, labels, FLAGS, boxes, confidences, classids, idxs, infer=False)
				count = (count + 1) % 6

			area = getDtc(FLAGS.name, height, width)
			print("area : ", area)
			if len(area) != 0:
				cv.polylines(frame, [area], True, (255, 0, 0), 1)

			cv.imshow('stream', frame)

			if cv.waitKey(1) & 0xFF == ord('q'):
				break
		vid.release()
		cv.destroyAllWindows()
	else:
		# Infer real-time on webcam
		count = 0

		vid = cv.VideoCapture('http://218.38.40.240:10515/?action=stream')
		while True:
			_, frame = vid.read()
			height, width = frame.shape[:2]

			if count == 0:
				frame, boxes, confidences, classids, idxs = infer_image(net, layer_names, \
		    						height, width, frame, colors, labels, FLAGS)
				count += 1
			else:
				frame, boxes, confidences, classids, idxs = infer_image(net, layer_names, \
		    						height, width, frame, colors, labels, FLAGS, boxes, confidences, classids, idxs, infer=False)
				count = (count + 1) % 6

			cv.imshow('webcam', frame)

			if cv.waitKey(1) & 0xFF == ord('q'):
				break
		vid.release()
		cv.destroyAllWindows()
