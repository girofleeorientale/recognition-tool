import numpy as np
import cv2 as cv
import sys
import csv
import math


imageName = str(sys.argv[1])


# find circle
imgC = cv.imread(imageName,0)
imgC = cv.medianBlur(imgC,5)
cimgC = cv.cvtColor(imgC,cv.COLOR_GRAY2BGR) 
circles = cv.HoughCircles(imgC, cv.HOUGH_GRADIENT, 1.2, 1000)
circles = np.uint16(np.around(circles))

print('circles: ', circles[0][0])

# get initial image with only oreo
img = cv.imread(imageName)
assert img is not None, "file could not be read"
mask = np.zeros(img.shape[:2],np.uint8)
bgdModel = np.zeros((1,65),np.float64)
fgdModel = np.zeros((1,65),np.float64)
# find x, y
rectX = circles[0][0][0] - 180
rectY = circles[0][0][1] - 170
# grab and cut image
rect = (rectX, rectY, 400, 400)
cv.grabCut(img,mask,rect,bgdModel,fgdModel,5,cv.GC_INIT_WITH_RECT)
mask2 = np.where((mask==2)|(mask==0),0,1).astype('uint8')
img = img*mask2[:,:,np.newaxis]

# find and draw contours
cv.imwrite('image.jpg',img)
modImg = cv.imread('image.jpg', cv.IMREAD_GRAYSCALE)  
thresh, BW = cv.threshold(modImg,50,255,cv.THRESH_BINARY + cv.THRESH_OTSU)
contours, hierarchy = cv.findContours(BW,  cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
temp = np.zeros((modImg.shape[0],modImg.shape[1],3), dtype = np.uint8)
#cv.drawContours(temp,contours, -1,(0,0,255),1)
# here: -1 draw all the contour points
cv.drawContours(temp,contours, -1,(0,0,255),3)

# eliminate unwanted contours
emptyMask = np.zeros(img.shape[:2], dtype=img.dtype)
for i in contours:
    area = cv.contourArea(i)
    if area > 200:
        x, y, w, h = cv.boundingRect(i)
        cv.drawContours(emptyMask, [i], 0, (255), -1)

result = cv.bitwise_and(img,img, mask= emptyMask)

# writing result with no unnecessary contours
cv.imwrite('result.jpg',result)
imgResult = cv.imread('result.jpg', cv.IMREAD_GRAYSCALE)  

# contours noiseless
thresh2, BW2 = cv.threshold(imgResult,50,255,cv.THRESH_BINARY + cv.THRESH_OTSU)
contours2, hierarchy = cv.findContours(BW2,  cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
tempNoiseless = np.zeros((imgResult.shape[0],imgResult.shape[1],3), dtype = np.uint8)
cv.drawContours(tempNoiseless,contours2, -1,(0,0,255),1)
cv.imwrite('resultNoiseless.jpg',tempNoiseless)
imgNoiseless = cv.imread('resultNoiseless.jpg', cv.IMREAD_GRAYSCALE)

# try : compare ideal VS shifted
imgIdeal = cv.imread('idealContours.jpg', cv.IMREAD_GRAYSCALE)
m1 = cv.matchShapes(imgIdeal, imgNoiseless, cv.CONTOURS_MATCH_I2, 0)
#print("comparison result : {}".format(m1))

def createAllContoursAray (contours):
    areasArray = []

    for i in contours:
        #for j in i:
            #cnt = j
            oneArea = cv.contourArea(i)
            areasArray.append(oneArea)
    
    return areasArray

contourArray = createAllContoursAray(contours2)


# find x, y of the circle center
xCircle = circles[0][0][0]
yCircle = circles[0][0][1]
radCircle = circles[0][0][2]

#foundCircleArea = 3.14*radCircle**2
#print('area of the first found circle', foundCircleArea)

def isDefectiveBiscuit (contours):
    isDefective = False
    minRadius = 0

    for i in contours:
        for j in i:
            cnt = j
            contoursX = cnt[0][0]
            contoursY = cnt[0][1]
            distanceToCenter = np.sqrt((np.square(xCircle - contoursX)) + (np.square(yCircle - contoursY)))
            if (distanceToCenter < radCircle-25) :
                isDefective = True
    return isDefective


def classifier (contours):
    if isDefectiveBiscuit(contours) :
        return 'defectueux'
    else :
        return 'entier'

resFinal = classifier(contours2)


def isShiftedBiscuit (contours):
    isShifted = False
    minRadius = 0

    for i in contours:
        for j in i:
            cnt = j
            contoursX = cnt[0][0]
            contoursY = cnt[0][1]
            distanceToCenter = np.sqrt((np.square(xCircle - contoursX)) + (np.square(yCircle - contoursY)))
            if (distanceToCenter > radCircle+30) :
                isShifted = True
    return isShifted

cv.imwrite('temp.jpg', tempNoiseless)

# looking for minimum enclosing circle
def findEnclosingCircle (contours):
    cpt = -1

    for i in contours:
        cnt = i
        (xEnclosing,yEnclosing),radiusEnclosing = cv.minEnclosingCircle(cnt)
        #print('area enclosing circle:', 3.14*radiusEnclosing**2)
        centerEnclosing = (int(xEnclosing),int(yEnclosing))
        radiusEnclosing = int(radiusEnclosing)
        cv.circle(temp,centerEnclosing,radiusEnclosing,(0,255,0),2)
        cpt+=1
    #print('distinct contours: ', cpt)
    return cpt

# looking for minimum enclosing circle
def findApproxContour (contours):
    for i in contours:
        cnt = i
        epsilon = 0.0009*cv.arcLength(cnt,True)
        approx = cv.approxPolyDP(cnt,epsilon,True)
        cv.drawContours(temp, [approx], -1, (0,255,0), 3)
        #print('area enclosing circle:', 3.14*radiusEnclosing**2)
    #print('distinct contours: ', cpt)
    cv.imwrite('tempApproxPoly.jpg', temp)


    

# transforms to prepare for lines detection
src = cv.imread("temp.jpg")

gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
ret, binary = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)

se = cv.getStructuringElement(cv.MORPH_RECT, (10, 10), (-1, -1))
binary = cv.morphologyEx(binary, cv.MORPH_OPEN, se)

cv.imwrite('binary.jpg', binary)


# try to detect lines  === temp === 
isThereLine = False
src = cv.imread('binary.jpg', cv.IMREAD_GRAYSCALE)
        
dst = cv.Canny(src, 50, 200, None, 3)
    
cdst = cv.cvtColor(dst, cv.COLOR_GRAY2BGR)
cdstP = np.copy(cdst)
    
lines = cv.HoughLines(dst, 1, np.pi / 180, 150, None, 0, 0)
pt1 = pt2 = 0
    
if lines is not None:
        for i in range(0, len(lines)):
            rho = lines[i][0][0]
            theta = lines[i][0][1]
            a = math.cos(theta)
            b = math.sin(theta)
            x0 = a * rho
            y0 = b * rho
            pt1 = (int(x0 + 1000*(-b)), int(y0 + 1000*(a)))
            pt2 = (int(x0 - 1000*(-b)), int(y0 - 1000*(a)))
            cv.line(cdst, pt1, pt2, (0,0,255), 3, cv.LINE_AA)

    
    
linesP = cv.HoughLinesP(dst, 1, np.pi / 180, 50, None, 80, 10)
    
if linesP is not None:
        for i in range(0, len(linesP)):
            l = linesP[i][0]
            cv.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0,0,255), 3, cv.LINE_AA)
            #print('a line was found')
            isThereLine = True

isShifted = isShiftedBiscuit(contours2)
#print('is shifted:', isShifted)

#cptEnclosing = findEnclosingCircle(contours2)
findApproxContour(contours2)

# try : compare ideal approx poly VS shifted
imgIdealPoly = cv.imread('idealApproxPoly1.jpg', cv.IMREAD_GRAYSCALE)
imgApproxPoly = cv.imread('tempApproxPoly.jpg', cv.IMREAD_GRAYSCALE)
m2 = cv.matchShapes(imgIdealPoly, imgApproxPoly, cv.CONTOURS_MATCH_I2, 0)
print("comparison result : {}".format(m1))

comparisonRounded = round(m1, 4)
comparisonPolyRounded = round(m2, 4)

# writing data to csv
header = ['name', 'shape comparison', 'contour area', 'min area']
header2 = ['name', 'isDefective']
data = [imageName, resFinal]
dataContours = [imageName, contourArray]
dataShifted = [imageName, isShifted]
dataShiftedWithShapeCmp = [imageName, comparisonRounded]
dataShiftedPoly = [imageName, comparisonPolyRounded]
#dataCptEnclosing = [imageName, cptEnclosing]

with open('decales.csv', 'a', encoding='UTF8') as f:
    writer = csv.writer(f)
#    writer.writerow(header2)
    writer.writerow(dataShiftedPoly)
#    writer.writerow(data2)
    
cv.imwrite('tempLine.jpg',cdstP)    
#cv.imshow("Source", src)
#cv.imshow("Detected Lines (in red) - Standard Hough Line Transform", cdst)
#cv.imshow("Detected Lines (in red) - Probabilistic Line Transform", cdstP)

print("contours array: ", createAllContoursAray(contours2))

#cv.imshow('after grab cut', img)
cv.imshow('temp contours', temp)
#cv.imshow('result', resFinal)
#cv.imshow('Lines', imageLine)


cv.waitKey(0)
cv.destroyAllWindows()