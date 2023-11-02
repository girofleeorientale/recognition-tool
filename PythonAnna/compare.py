import cv2
import numpy as np

#result of this comparison is false
img1 = cv2.imread('img/ciseaux.png',0)
img2 = cv2.imread('img/mange.png',0)

ret, thresh = cv2.threshold(img1, 127, 255,0)
ret, thresh2 = cv2.threshold(img2, 127, 255,0)
contours,hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
cnt1 = contours[0]
contours,hierarchy = cv2.findContours(thresh2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
cnt2 = contours[0]

ret = cv2.matchShapes(cnt1,cnt2, cv2.CONTOURS_MATCH_I2,0)
print (ret)