import numpy as np
import argparse
import cv2 as cv
import subprocess
import time
import os

def show_image(img):
    cv.imshow("Image", img)
    cv.waitKey(0)

def draw_labels_and_boxes(img, boxes, confidences, classids, idxs, colors, labels, car_in_lane, last_data):
    # If there are any detections
    if len(idxs) > 0:
        for i in idxs.flatten():
            # Get the bounding box coordinates
            x, y = boxes[i][0], boxes[i][1]
            w, h = boxes[i][2], boxes[i][3]
            
            # Get the unique color for this class
            color = [int(c) for c in colors[classids[i]]]

            # Draw the bounding box rectangle and label on the image
            cv.rectangle(img, (x, y), (x+w, y+h), color, 1)
            text = "{}".format(labels[classids[i]])
            cv.putText(img, text, (x, y-5), cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)


    for i, car in enumerate(car_in_lane):
        car_in_lane_text = f"lane({i + 1}) : {len(car)}"
        cv.putText(img, car_in_lane_text, (10, 20 + (i * 20)), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)


    return img

#def generate_boxes_confidences_classids(outs, height, width, tconf):
def generate_boxes_confidences_classids(outs, height, width, tconf, labels, ldtcs=None):
    boxes = []
    confidences = []
    classids = []
    car_in_lane = [[] for i in range(len(ldtcs))]
    for out in outs:
        for detection in out:
            #a = input('GO!')

            # Get the scores, classid, and the confidence of the prediction
            scores = detection[5:]
            classid = np.argmax(scores)
            confidence = scores[classid]
            
            # Consider only the predictions that are above a certain confidence level
            if confidence > tconf:
                # TODO Check detection
                box = detection[0:4] * np.array([width, height, width, height])
                centerX, centerY, bwidth, bheight = box.astype('int')

                # Using the center x, y coordinates to derive the top
                # and the left corner of the bounding box
                x = int(centerX - (bwidth / 2))
                y = int(centerY - (bheight / 2))

                #print("%s - x : %d, y : %d" % (labels[classid], centerX, centerY))

                #objectX, objectY는 박스의 중앙 아래를 의미하며 차량인식좌표로 사용됨
                objectX = centerX
                objectY = int(centerY + (bheight / 2))
                for i,ldtc in enumerate(ldtcs,0):
                    inside_pixel=cv.pointPolygonTest(ldtc,(objectX, objectY),True)
                    if inside_pixel>=0:
                        # 순서대로 bycycle, car, motorbike, bus, truck
                        if classid==1 or classid==2 or classid==3 or classid==5 or classid==8:
                            last_data=car_in_lane[i]
                            car_in_lane[i].append((classid, objectX, objectY))



                # Append to list
                boxes.append([x, y, int(bwidth), int(bheight)])
                confidences.append(float(confidence))
                classids.append(classid)

    return boxes, confidences, classids, car_in_lane

def infer_image(net, layer_names, height, width, main, img, colors, labels, FLAGS, last_data,
            boxes=None, confidences=None, classids=None, idxs=None, infer=True, ldtcs=None):
    
    if infer:
        # 입력 이미지에서 블롭 구성
        blob = cv.dnn.blobFromImage(main, 1 / 255.0, (416, 416),
                        swapRB=True, crop=False)

        # YOLO 개체 탐지기의 전방 통과 수행
        net.setInput(blob)

        # 출력 계층에서 출력 가져오기
        start = time.time()
        outs = net.forward(layer_names)
        end = time.time()

        if FLAGS.show_time:
            print ("[INFO] YOLOv3 took {:6f} seconds".format(end - start))

        
        # boxes, confidences, and classIDs 생성
        boxes, confidences, classids, car_in_lane = generate_boxes_confidences_classids(outs, height, width, FLAGS.confidence, labels,ldtcs=ldtcs)
        
        # 겹치는 경계 상자 억제를 위해 최대값이 아닌 억제 적용
        idxs = cv.dnn.NMSBoxes(boxes, confidences, FLAGS.confidence, FLAGS.threshold)

    if boxes is None or confidences is None or idxs is None or classids is None:
        raise Exception('[ERROR] Required variables are set to None before drawing boxes on images.')
        
    # Draw labels and boxes on the image
    img = draw_labels_and_boxes(img, boxes, confidences, classids, idxs, colors, labels, car_in_lane, last_data)

    return img, boxes, confidences, classids, idxs, car_in_lane
