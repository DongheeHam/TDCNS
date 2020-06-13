import numpy as np
import argparse
import cv2 as cv
import subprocess
import time
import os

def show_image(img):
    cv.imshow("Image", img)
    cv.waitKey(0)

def draw_labels_and_boxes(img, boxes, confidences, classids, idxs, colors, labels):
    # If there are any detections
    if len(idxs) > 0:
        for i in idxs.flatten():
            # Get the bounding box coordinates
            x, y = boxes[i][0], boxes[i][1]
            w, h = boxes[i][2], boxes[i][3]
            
            # Get the unique color for this class
            color = [int(c) for c in colors[classids[i]]]

            # Draw the bounding box rectangle and label on the image
            cv.rectangle(img, (x, y), (x+w, y+h), color, 2)
            text = "{}: {:4f}".format(labels[classids[i]], confidences[i])
            cv.putText(img, text, (x, y-5), cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)


    return img

#def generate_boxes_confidences_classids(outs, height, width, tconf):
def generate_boxes_confidences_classids(outs, height, width, tconf, labels, lanes=None):
    boxes = []
    confidences = []
    classids = []

    for out in outs:
        for detection in out:
            #print (detection)
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

                if lanes!=None:
                    for lane in lanes:
                        inside=cv.pointPolygonTest(lane,(x, y),True)
                        print("inside = ",inside)


                # Append to list
                boxes.append([x, y, int(bwidth), int(bheight)])
                confidences.append(float(confidence))
                classids.append(classid)

    return boxes, confidences, classids

def infer_image(net, layer_names, height, width, main, img, colors, labels, FLAGS,
            boxes=None, confidences=None, classids=None, idxs=None, infer=True, lanes=None):
    
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
        boxes, confidences, classids = generate_boxes_confidences_classids(outs, height, width, FLAGS.confidence, labels,lanes=lanes)
        
        # 겹치는 경계 상자 억제를 위해 최대값이 아닌 억제 적용
        idxs = cv.dnn.NMSBoxes(boxes, confidences, FLAGS.confidence, FLAGS.threshold)

    if boxes is None or confidences is None or idxs is None or classids is None:
        raise '[ERROR] Required variables are set to None before drawing boxes on images.'
        
    # Draw labels and boxes on the image
    img = draw_labels_and_boxes(img, boxes, confidences, classids, idxs, colors, labels)

    return img, boxes, confidences, classids, idxs
