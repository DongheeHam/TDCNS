# import the necessary packages
#from pyimagesearch.motion_detection import SingleMotionDetector
from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template
import threading
import argparse
import datetime
import imutils
import time
import cv2

# 출력 프레임의 스레드 세이프 교환을 보장하기 위해 사용되는 출력 프레임 및 잠금 초기화
# (여러 브라우저/펌프가 스트림을 볼 때 발생)
outputFrame = None
lock = threading.Lock()
# 플라스크 객체 초기화
app = Flask(__name__)
# 비디오 스트림을 초기화하고 카메라 센서를 예열할 수 있도록 하십시오.
#vs = VideoStream(usePiCamera=1).start()
vs = VideoStream(src=0).start()
time.sleep(2.0)

@app.route("/")
def index():
    # return the rendered template
    return render_template("index.html")

# def detect_motion(frameCount):
#     # 비디오 스트림, 출력 프레임 및 잠금 변수에 대한 글로벌 참조 확보
#     global vs, outputFrame, lock
#     # initialize the motion detector and the total number of frames
#     # 지금까지 읽은 인식기와 총 프레임 수를 초기화한다.
#     # md = SingleMotionDetector(accumWeight=0.1)
#
#     total = 0
#     # loop over frames from the video stream
#     while True:
#         # read the next frame from the video stream, resize it,
#         # convert the frame to grayscale, and blur it
#         frame = vs.read()
#         frame = imutils.resize(frame, width=400)
#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         gray = cv2.GaussianBlur(gray, (7, 7), 0)
#         # grab the current timestamp and draw it on the frame
#         timestamp = datetime.datetime.now()
#         cv2.putText(frame, timestamp.strftime(
#             "%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
#         # if the total number of frames has reached a sufficient
#         # number to construct a reasonable background model, then
#         # continue to process the frame
#         if total > frameCount:
#             # detect motion in the image
#             motion = md.detect(gray)
#             # check to see if motion was found in the frame
#             if motion is not None:
#                 # unpack the tuple and draw the box surrounding the
#                 # "motion area" on the output frame
#                 (thresh, (minX, minY, maxX, maxY)) = motion
#                 cv2.rectangle(frame, (minX, minY), (maxX, maxY),
#                               (0, 0, 255), 2)
#
#         # update the background model and increment the total number
#         # of frames read thus far
#         md.update(gray)
#         total += 1
#         # acquire the lock, set the output frame, and release the
#         # lock
#         with lock:
#             outputFrame = frame.copy()


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

@app.route("/video_feed")
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    return Response(generate(),
        mimetype = "multipart/x-mixed-replace; boundary=frame")

# check to see if this is the main thread of execution
if __name__ == '__main__':
    # construct the argument parser and parse command line arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=True, default="",
        help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, required=True, default=8081,
        help="ephemeral port number of the server (1024 to 65535)")
    ap.add_argument("-f", "--frame-count", type=int, default=32,
        help="# of frames used to construct the background model")
    args = vars(ap.parse_args())
    # start a thread that will perform motion detection
    t = threading.Thread(target=detect_motion, args=(
        args["frame_count"],))
    t.daemon = True
    t.start()
    # start the flask app
    app.run(host=args["ip"], port=args["port"], debug=True,
        threaded=True, use_reloader=False)
# release the video stream pointer
vs.stop()