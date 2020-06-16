# import numpy as np
# import argparse
# import cv2 as cv
# import matplotlib.pyplot as plt
#
# if __name__ == '__main__':
#     parser = argparse.ArgumentParser()
#     parser.add_argument('-f', '--file',
#                         type=str,
#                         default='Sample1.avi')
#     parser.add_argument('-p', '--path',
#                         type=str,
#                         default='./picture/')
#     parser.add_argument('-st', '--stream',
#                         type=str)
#     FLAGS, unparsed = parser.parse_known_args()
#     if FLAGS.file:
#         cap = cv.VideoCapture(FLAGS.path + FLAGS.file)
#     elif FLAGS.stream:
#         cap = cv.VideoCapture(FLAGS.stream)
#
#
#     ret, image = cap.read()
#     height, width = image.shape[:2]
#     print(height, width)
#     """ 마스크 생성 """
#     # create a zero array
#     stencil = np.zeros_like(image[:, :, 0])
#
#     # 다각형 좌표 지정
#     polygon = np.array([[450, height], [450, 170], [650, 180], [900, height]])
#
#     # 다각형 채우기
#     cv.fillConvexPoly(stencil, polygon, 1)
#
#     # 합치기
#     img = cv.bitwise_and(image, image, mask=stencil)
#
#     """ 이미지 전처리 """
#     # 이미지 임계값 적용
#     ret, thresh = cv.threshold(img, 130, 145, cv.THRESH_BINARY)
#
#     # Hough Line Transformation 허프 라인 변환
#     #lines = cv.HoughLinesP(thresh, 1, np.pi / 180, 30, maxLineGap=200)
#
#     # 원본 이미지의 사본을 만들다.
#     #dmy = image[:, :, 0].copy()
#
#     # draw Hough lines
#     # for line in lines:
#     #     x1, y1, x2, y2 = line[0]
#     #     cv.line(dmy, (x1, y1), (x2, y2), (255, 0, 0), 3)
#     print(image.shape)
#     plt.figure(figsize=(10, 10))
#     plt.imshow(image)
#     plt.show()
#
