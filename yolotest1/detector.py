import numpy as np
import cv2 as cv
import time

class Detector:
    def __init__(self, net, layer_names, FLAGS, vid, dtc, ldtcs, labels, height=None, width=None):
        self.net = net
        self.layer_names = layer_names
        self.FLAGS = FLAGS
        self.vid = vid
        self.dtc = dtc
        self.ldtcs = ldtcs
        self.labels = labels
        self.height = height
        self.width = width
        # 라벨 색상 랜덤 초기화
        self.colors = np.random.randint(0, 255, size=(len(self.labels), 3), dtype='uint8')

    def setHeightAndWidth(self, height, width):
        self.height = height
        self.width = width

    def getDtcFrame(self, frame):
        # frame 크기의 검은화면 생성
        stencil = np.zeros_like(frame[:, :, 0])
        # 검은 화면에 흰색 다각형(dtc) 채우기
        cv.fillConvexPoly(stencil, self.dtc, 1)
        # 합치기
        img = cv.bitwise_and(frame, frame, mask=stencil)
        return img

    def infer_image(self, frame, infer=True):
        if infer:
            # 입력 이미지에서 인식할 부분만 걸러냄
            main = self.getDtcFrame(frame)

            # 걸러낸 이미지에서 블롭 구성
            blob = cv.dnn.blobFromImage(main, 1 / 255.0, (416, 416), swapRB=True, crop=False)

            # YOLO 개체 탐지기의 전방 통과 수행
            self.net.setInput(blob)

            # 출력 계층에서 출력 가져오기
            start = time.time()
            outs = self.net.forward(self.layer_names)
            end = time.time()

            # 걸린시간 출력
            if self.FLAGS.show_time:
                print("[INFO] YOLOv3 took {:6f} seconds".format(end - start))

            # boxes, confidences, and classIDs 생성
            boxes, confidences, classids, car_in_lane = self.generate_boxes_confidences_classids(outs)

            # 겹치는 경계 상자 억제를 위해 최대값이 아닌 억제 적용
            idxs = cv.dnn.NMSBoxes(boxes, confidences, self.FLAGS.confidence, self.FLAGS.threshold)

            self.last_boxes, self.last_confidences, self.last_classids, self.last_car_in_lane, self.idxs = \
                (boxes, confidences, classids, car_in_lane, idxs)
        else:
            boxes, confidences, classids, car_in_lane, idxs = \
                (self.last_boxes, self.last_confidences, self.last_classids, self.last_car_in_lane, self.idxs)
        if boxes is None or confidences is None or idxs is None or classids is None:
            raise Exception('[ERROR] frame에 box를 그릴 때 필요한 변수 없음.')

        frame = self.draw_labels_and_boxes(frame, boxes, confidences, classids, idxs, car_in_lane)

        return frame

    def generate_boxes_confidences_classids(self, outs):
        boxes = []
        confidences = []
        classids = []
        car_in_lane = [[] for i in range(len(self.ldtcs))]

        for out in outs:
            for detection in out:
                # 예측한 점수, 등급 및 신뢰도를 얻음
                scores = detection[5:]
                classid = np.argmax(scores)
                confidence = scores[classid]

                # 특정 신뢰 수준을 초과하는 예측만 고려함
                if confidence > self.FLAGS.confidence:
                    box = detection[0:4] * np.array([self.width, self.height, self.width, self.height])
                    centerX, centerY, bwidth, bheight = box.astype('int')

                    # 중심 x, y 좌표를 사용하여 경계 상자의 상단 및 왼쪽 모서리를 얻음
                    x = int(centerX - (bwidth / 2))
                    y = int(centerY - (bheight / 2))

                    # print("%s - x : %d, y : %d" % (labels[classid], centerX, centerY))

                    # objectX, objectY는 박스의 중앙 아래를 의미하며 차량인식좌표로 사용됨
                    objectX = centerX
                    objectY = int(centerY + (bheight / 2))
                    for i, ldtc in enumerate(self.ldtcs, 0):
                        inside_pixel = cv.pointPolygonTest(ldtc, (objectX, objectY), True)
                        if inside_pixel >= 0:
                            # 순서대로 bycycle, car, motorbike, bus, truck
                            if classid == 1 or classid == 2 or classid == 3 or classid == 5 or classid == 8:
                                last_data = car_in_lane[i]
                                car_in_lane[i].append((classid, objectX, objectY))

                    # Append to list
                    boxes.append([x, y, int(bwidth), int(bheight)])
                    confidences.append(float(confidence))
                    classids.append(classid)

        return boxes, confidences, classids, car_in_lane

    def draw_labels_and_boxes(self, frame, boxes, confidences, classids, idxs, car_in_lane):
        # 탐지된 객체가 있는 경우
        if len(idxs) > 0:
            for i in idxs.flatten():
                # Get the bounding box coordinates
                x, y = boxes[i][0], boxes[i][1]
                w, h = boxes[i][2], boxes[i][3]

                # Get the unique color for this class
                color = [int(c) for c in self.colors[classids[i]]]

                # Draw the bounding box rectangle and label on the image
                cv.rectangle(frame, (x, y), (x + w, y + h), color, 1)
                text = "{}".format(self.labels[classids[i]])
                cv.putText(frame, text, (x, y - 5), cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        for i, car in enumerate(car_in_lane):
            car_in_lane_text = f"lane({i + 1}) : {len(car)}"
            cv.putText(frame, car_in_lane_text, (10, 20 + (i * 20)), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

        return frame

    def show(self, frame):
        # dtc 그리기
        cv.polylines(frame, [self.dtc], True, (255, 0, 0), 1)

        # ldtc 그리기
        for ldtc in self.ldtcs:
            cv.polylines(frame, [ldtc], True, (0, 255, 0), 1)

        cv.imshow('video', frame)