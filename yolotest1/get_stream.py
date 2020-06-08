import cv2
import argparse
#cap = cv2.VideoCapture('http://218.38.40.240:10515/?action=stream')
#cap = cv2.VideoCapture('rtmp://210.179.218.51/live/238.stream')
cap = cv2.VideoCapture('rtmp://210.179.218.52/live/140.stream')
if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-st', '--stream-path',
		type=str,
		help='The path to the video file')
	FLAGS, unparsed = parser.parse_known_args()
	if FLAGS.stream_path:
		cap = cv2.VideoCapture(FLAGS.stream_path)
	else:
		cap = cv2.VideoCapture('http://218.38.40.240:10515/?action=stream')
	while True:
	  ret, frame = cap.read()
	  print(frame)
	  cv2.imshow('Video', frame)

	  if cv2.waitKey(1) == 27:
	    exit(0)
