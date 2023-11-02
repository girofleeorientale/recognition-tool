import numpy as np
import cv2 as cv

img = cv.imread('mange.jpg',0)
img = cv.medianBlur(img,5)
cimg = cv.cvtColor(img,cv.COLOR_GRAY2BGR)

# with minDist = 1000 detects one (entire) circle (+ fissure); minDist = 200 too small!

#circles = cv.HoughCircles(img,cv.HOUGH_GRADIENT,1,1000,
#                            param1=50,param2=30,minRadius=0,maxRadius=0)

circles = cv.HoughCircles(img, cv.HOUGH_GRADIENT, 1.2, 1000)

circles = np.uint16(np.around(circles))
for i in circles[0,:]:
    # draw the outer circle
    cv.circle(cimg,(i[0],i[1]),i[2],(0,255,0),2)
    # draw the center of the circle
    cv.circle(cimg,(i[0],i[1]),2,(0,0,255),3)
cv.imshow('detected circles',cimg)
cv.waitKey(0)
cv.destroyAllWindows()