import numpy as np
import cv2 as cv
import sys
import csv

# here: find circle + create mask based on it
# the aim: extract the image of interest (one oreo), then draw its contours

imageName = str(sys.argv[1])

# find circle
try:
    imgC = cv.imread(imageName,0)
    imgC = cv.medianBlur(imgC,5)
    cimgC = cv.cvtColor(imgC,cv.COLOR_GRAY2BGR) 
    circles = cv.HoughCircles(imgC, cv.HOUGH_GRADIENT, 1.2, 1000)
    circles = np.uint16(np.around(circles))
except:
    print('[RESULT] Not an Oreo')
    exit(1)

# reference image
imgIdeal = cv.imread('ideal.jpg', cv.IMREAD_GRAYSCALE)

# apply grabcut
img = cv.imread(imageName)
assert img is not None, "file could not be read"
mask = np.zeros(img.shape[:2],np.uint8)
bgdModel = np.zeros((1,65),np.float64)
fgdModel = np.zeros((1,65),np.float64)

rectX = circles[0][0][0] - 180
rectY = circles[0][0][1] - 170

rect = (rectX, rectY, 400, 400)
cv.grabCut(img,mask,rect,bgdModel,fgdModel,5,cv.GC_INIT_WITH_RECT)
mask2 = np.where((mask==2)|(mask==0),0,1).astype('uint8')
img = img*mask2[:,:,np.newaxis]

# eliminate noise

cv.imwrite('image.jpg',img)
modImg = cv.imread('image.jpg', cv.IMREAD_GRAYSCALE)  
thresh, BW = cv.threshold(modImg,50,255,cv.THRESH_BINARY + cv.THRESH_OTSU)
contours, hierarchy = cv.findContours(BW,  cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
temp = np.zeros((modImg.shape[0],modImg.shape[1],3), dtype = np.uint8)
cv.drawContours(temp,contours, -1,(0,0,255),1)
#cv.imshow('Original Image',img)

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


kernel = cv.getStructuringElement(cv.MORPH_RECT,(5,5))
dilated = cv.dilate(modImg, kernel)
contours, _ = cv.findContours(dilated.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

# finding the maximum area in contours
def findArea (contours):
    maxArea = 0
    for counter in contours:
        area = cv.contourArea(counter)
        if area > 1000:
            if area > maxArea:
                maxArea = area
    return maxArea

def findMinArea (contours) :
    minArea = cv.contourArea(contours[0]) 
    for counter in contours:
        area = cv.contourArea(counter)
        if area > 1000:
            if area < minArea:
                minArea = area
    return minArea

# contours noiseless
thresh2, BW2 = cv.threshold(imgResult,50,255,cv.THRESH_BINARY + cv.THRESH_OTSU)
contours2, hierarchy = cv.findContours(BW2,  cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
tempNoiseless = np.zeros((imgResult.shape[0],imgResult.shape[1],3), dtype = np.uint8)
cv.drawContours(tempNoiseless,contours2, -1,(0,0,255),1)
cv.imwrite('resultNoiseless.jpg',tempNoiseless)
imgNoiseless = cv.imread('resultNoiseless.jpg', cv.IMREAD_GRAYSCALE)  
areaNoiseless = findArea(contours2)
print('img qarea noiseless: ', areaNoiseless)


# corresponding abstract circle area
circleArea = (circles[0][0][2]**2)*3.14
circleAreaRounded = round(circleArea, 2)

# matching part between reference image and the image without noise
#m1 = cv.matchShapes(imgIdeal, imgResult, cv.CONTOURS_MATCH_I2, 0)
m1 = cv.matchShapes(imgIdeal, imgResult, cv.CONTOURS_MATCH_I2, 0)
print("comparison result : {}".format(m1))

# INTERMEDIATE CONCLUSION:
# matchSapes efficient for cracks,
# contourArea efficient for eated.

def classifier (matchShape, area) :
    if matchShape < 0.01:
        return 'entier'
    elif matchShape > 0.05:
        return 'fissure'
    elif area < 81000 :
        return 'mange'
    elif area < 83700 and area >= 8100:
        if matchShape < 0.04:
            return 'mange'
        else :
            return 'fissure'
    else : return 'entier'


# writing data to csv
comparisonRounded = round(m1, 4)
maxArea = findArea(contours2)
minArea = findMinArea(contours2)
resToWrite = classifier (comparisonRounded, maxArea)

header = ['name', 'shape comparison', 'contour area', 'min area']
data = [imageName, comparisonRounded, maxArea, minArea]
data2 = [imageName, resToWrite]

with open('data.csv', 'a', encoding='UTF8') as f:
    writer = csv.writer(f)
#    writer.writerow(header)
    writer.writerow(data)
#    writer.writerow(data2)


#print('contour\'s area:', cv.contourArea(contours[0]))
print('contour\'s MAX area:', maxArea)
print('contour\'s APPROX area:', cv.contourArea(contours[0]))
print('circle area:', circleArea)
print('circle radius:', circles[0][0][2])
perimeter = cv.arcLength(contours[0],True)
print('contours perimeter:', perimeter)
print('[RESULT] ', classifier(comparisonRounded, maxArea))
#perimeterCircle = circles[0][0][2]*2*3.14
#print('circle perimeter:', perimeterCircle)

#cv.imshow('Contours Drawn',temp)
#cv.imshow('masked img', img)
#cv.imshow('result img', tempNoiseless)
cv.waitKey(0)
cv.destroyAllWindows()
