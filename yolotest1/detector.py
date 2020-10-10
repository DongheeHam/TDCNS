import numpy as np
import cv2 as cv
import time
import sys

class Detector:
    def __init__(self, net, layer_names, FLAGS, dtc, ldtcs, counter, labels,\
                 sizecut, height=None, width=None):
        self.net = net
        self.layer_names = layer_names
        self.FLAGS = FLAGS
        self.dtc = dtc
        self.ldtcs = ldtcs
        self.counter = counter
        self.labels = labels
        self.height = height
        self.width = width
        self.sizecut=sizecut

        # count 관련
        # 차선개수[대형수,소형수]
        self.lane_count = [[0,0] for _ in counter]

        """
        내가 시도했던 카운팅 알고리즘은 멈춘 차가 카운팅존에 걸쳐서 계속 카운팅되는걸 막으려고 
        3개 frame동안 카운팅 존에 있다가 나가고 3개 프레임동안 카운팅존에 없으면 +1 카운팅하는걸 시도했는데
        차가 나간 후 3개 프레임이 지나기 전 다음차가 들어오면 카운팅이 안되서 걍 1개프레임만 들어왔다가 나가도 카운팅
        하게끔 해놨음
        """
        self.last_car = [None for _ in counter]
        self.car_in_lane_counter = [0 for _ in counter]
        self.count_flag = False
        self.last_color = None

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
            # 입력 이미지에서 인식할 부분(dtc)만 걸러냄
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
                print("[INFO]n YOLOv3 took {:6f} seconds".format(end - start))

            # boxes, confidences, and classIDs 생성
            boxes, confidences, classids = self.generate_boxes_confidences_classids(outs)



            # 이번 프레임의 차선별 차량 대기열 정보를 저장할 변수 선언
            car_in_lane = [[] for i in range(len(self.ldtcs))]

            # 겹치는 경계 상자 억제를 위해 최대값이 아닌 억제 적용
            # TODO 상수를 조절해 겹친녀석을 더 확실하게 제거할 방법이 있나 연구해봐야 함
            # http://blog.naver.com/PostView.nhn?blogId=sogangori&logNo=220993971883&parentCategoryNo=6&categoryNo=&viewDate=&isShowPopularPosts=true&from=search
            idxs = cv.dnn.NMSBoxes(boxes, confidences, self.FLAGS.confidence, self.FLAGS.threshold)

            self.last_boxes, self.last_confidences, self.last_classids, self.last_car_in_lane, self.idxs = \
                (boxes, confidences, classids, car_in_lane, idxs)
        else:
            boxes, confidences, classids, car_in_lane, idxs = \
                (self.last_boxes, self.last_confidences, self.last_classids, self.last_car_in_lane, self.idxs)
        if boxes is None or confidences is None or idxs is None or classids is None:
            raise Exception('[ERROR] frame에 box를 그릴 때 필요한 변수 없음.')

        frame = self.draw_labels_and_boxes(frame, boxes, confidences, classids, idxs, car_in_lane, infer)

        return frame

    def generate_boxes_confidences_classids(self, outs):
        boxes = []
        confidences = []
        classids = []
        a=0
        for out in outs:
            # if a==0:
            #     print(out)
            a+=1
            for detection in out:
                # 예측한 점수, 등급 및 신뢰도를 얻음
                scores = detection[5:]
                classid = np.argmax(scores)
                confidence = scores[classid]


                # 특정 신뢰 수준을 초과하는 예측만 고려함
                if confidence > self.FLAGS.confidence:
                    box = detection[0:4] * np.array([self.width, self.height, self.width, self.height])
                    #print("box : ", box)
                    centerX, centerY, bwidth, bheight = box.astype('int')

                    # 중심 x, y 좌표를 사용하여 경계 상자의 상단 및 왼쪽 모서리를 얻음
                    x = int(centerX - (bwidth / 2))
                    y = int(centerY - (bheight / 2))

                    # print("%s - x : %d, y : %d" % (labels[classid], centerX, centerY))

                    # objectX, objectY는 박스의 중앙 아래를 의미하며 차량인식좌표로 사용됨
                    objectX = centerX
                    objectY = int(centerY + (bheight / 2))

                    # for i, ldtc in enumerate(self.ldtcs, 0):
                    #     inside_pixel = cv.pointPolygonTest(ldtc, (objectX, objectY), True)
                    #     if inside_pixel >= 0:
                    #         # 순서대로 bycycle, car, motorbike, bus, truck
                    #         if classid == 1 or classid == 2 or classid == 3 or classid == 5 or classid == 7:
                    #             last_data = car_in_lane[i]
                    #             car_in_lane[i].append((classid, objectX, objectY))

                    # Append to list
                    boxes.append([x, y, int(bwidth), int(bheight), objectX, objectY])
                    confidences.append(float(confidence))
                    classids.append(classid)
        # print("last_car:",self.last_car)
        # print("car_in_lane_counter:", self.car_in_lane_counter)
        # print("lane_count:", self.lane_count)
        return boxes, confidences, classids

    def draw_labels_and_boxes(self, frame, boxes, confidences, classids, idxs, car_in_lane, infer):
        # 탐지된 객체가 있는 경우
        #print(len(idxs))
        if len(idxs) > 0:

            # 각각의 차선(ldtc)별로 해당 차선에 차량이 있는지 판단하기 위함.
            for j, ldtc in enumerate(self.ldtcs, 0):
                lane_flag=False

                # 인식한 결과물 모두를 탐색함.
                for i in idxs.flatten():
                    # Get the bounding box coordinates
                    x, y = boxes[i][0], boxes[i][1]
                    w, h = boxes[i][2], boxes[i][3]

                    # Get the unique color for this class
                    color = [int(c) for c in self.colors[classids[i]]]



                    if infer :
                        # 순서대로 bycycle, car, motorbike, bus, truck고 차일때만 데이터로 활용할 것이기 때문에 다른 객체는 걸러냄.
                        if classids[i] == 1 or classids[i] == 2 or classids[i] == 3 or classids[i] == 5 or classids[i] == 7:

                            # 현재 차선 (제일 바깥쪽 for문에서 탐색중인 차선)에 차량이 포함되어있는지 판단하는 함수
                            # cv.pointPolygonTest는 첫번째 매개변수(다각형)안에 두번째 매개변수(점)가 포함되어 있는지 판단함.
                            # 정확히 기억이 안나는데 return값이 0보다 크면 포함된다는거같음. 자세한건 opencv도큐먼트 확인할것
                            inside_ldtc = cv.pointPolygonTest(ldtc, (boxes[i][4], boxes[i][5]), True)

                            # 현재 차선에 현재 탐색중인 차량이 있다면
                            if inside_ldtc >= 0:
                                # 차선별 차량 대기열 변수에 현재 차량을 추가함
                                car_in_lane[j].append((classids[i], boxes[i][4], boxes[i][5]))

                            # print(j,i)
                            # print(boxes)
                            # print(self.counter)

                            # 바로 위의 insite_ldtc와 같은 방법으로 counter안에 차량이 있는지 판단
                            # 그리고 그 아래는 카운팅존에서 나갈때 +1카운트 하기 위한 알고리즘임
                            inside_counter = cv.pointPolygonTest(self.counter[j], (boxes[i][4], boxes[i][5]), True)
                            if inside_counter >= 0:
                                lane_flag=True
                                self.last_car[j] = boxes[i]
                                if self.car_in_lane_counter[j]>=0 and self.car_in_lane_counter[j] <1:
                                    self.car_in_lane_counter[j] += 1
                                    if self.car_in_lane_counter[j]==1:
                                        self.count_flag = True

                    # 인식한 차량을 frame image에 덮어 그리는것
                    cv.circle(frame, (boxes[i][4], boxes[i][5]), 4,color,2)
                    # Draw the bounding box rectangle and label on the image
                    cv.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    text = f"{self.labels[classids[i]]}, {w}, {h}"
                    cv.putText(frame, text, (x, y - 5), cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

                if infer:
                    # 여기도 차량을 카운팅하기 위한 알고리즘
                    if not lane_flag:
                        if self.car_in_lane_counter[j] > 0:
                            self.car_in_lane_counter[j] -= 1
                            if self.car_in_lane_counter[j] == 0:
                                #if self.count_flag:
                                if self.last_car[j][3] > self.sizecut:
                                    self.lane_count[j][0]+=1
                                else:
                                    self.lane_count[j][1] += 1
                                self.count_flag = False
                counter_color=(0,255,0)
                if self.car_in_lane_counter[j] >0:
                    counter_color = (0, 0, 255)
                cv.polylines(frame, [self.counter[j]], True, counter_color, 1)
        else:
            # print(len(self.ldtcs))
            # print(len(self.counter))
            for j, ldtc in enumerate(self.counter, 0):
                counter_color = (0, 255, 0)
                cv.polylines(frame, [self.counter[j]], True, counter_color, 1)

        # 대기열 텍스트 출력
        car_in_lane_text_ = ""
        for i, car in enumerate(car_in_lane):
            car_in_lane_text = f"lane({i + 1}) : {[self.labels[c] for c,_,_ in car ]}"
            cv.putText(frame, car_in_lane_text, (10, 20 + (i * 20)), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

            # 카운트 출력
            car_in_lane_text_ += f"lane {i+1} [ big :{self.lane_count[i][0]}, small : {self.lane_count[i][1]} ]| "

        cv.putText(frame, car_in_lane_text_, (10, 100), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

        return frame

    def show(self, frame):
        # dtc 그리기
        cv.polylines(frame, [self.dtc], True, (255, 0, 0), 1)

        # ldtc 그리기
        #for ldtc in self.ldtcs:
        #    cv.polylines(frame, [ldtc], True, (0, 255, 0), 1)
        # for aCounter in self.counter:
        #     cv.polylines(frame, [aCounter], True, (0, 255, 0), 1)

        cv.imshow('video', frame)
        #sys.stdout.write(frame.tostring())
        #sys.stdout.buffer.write(frame.tobytes())