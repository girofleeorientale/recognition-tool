import numpy as np
import cv2 as cv
import sys
import csv
import math


#imageName = str(sys.argv[1])


import time
start = time.time()
imageName = "img/mange3.jpg"



def AnalyseImageOpenCV(imageName):
    # find circle
    imgC = cv.imread(imageName, 0)
    imgC = cv.medianBlur(imgC,5)
    cimgC = cv.cvtColor(imgC,cv.COLOR_GRAY2BGR) 
    circles = cv.HoughCircles(imgC, cv.HOUGH_GRADIENT, 1.2, 1000)
    
    if circles is None:
        print('stop')
        exit(0)
        
    circles = np.uint16(np.around(circles))
    
    
    # get initial image with only oreo  TODO : see if possible to reuse line 12
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
    
    # find x, y of the circle center
    xCircle = circles[0][0][0]
    yCircle = circles[0][0][1]
    radCircle = circles[0][0][2]
    
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
    
    # try : compare ideal approx poly VS shifted
    imgIdealPoly = cv.imread('idealApproxPoly1.jpg', cv.IMREAD_GRAYSCALE)
    imgApproxPoly = cv.imread('tempApproxPoly.jpg', cv.IMREAD_GRAYSCALE)
    m2 = cv.matchShapes(imgIdealPoly, imgApproxPoly, cv.CONTOURS_MATCH_I2, 0)
    print("comparison result : {}".format(m2))
    
    def classifier (contours):
        if isDefectiveBiscuit(contours) :
            findApproxContour(contours)
            imgIdealPoly = cv.imread('idealApproxPoly1.jpg', cv.IMREAD_GRAYSCALE)
            imgApproxPoly = cv.imread('tempApproxPoly.jpg', cv.IMREAD_GRAYSCALE)
            m2 = cv.matchShapes(imgIdealPoly, imgApproxPoly, cv.CONTOURS_MATCH_I2, 0)
            comparisonPolyRounded = round(m2, 4)
    
            if comparisonPolyRounded > 0.2:
                return 'fissuré'
            else :
                return 'mangé'
        else :
            findApproxContour(contours)
            imgIdealPoly = cv.imread('idealApproxPoly1.jpg', cv.IMREAD_GRAYSCALE)
            imgApproxPoly = cv.imread('tempApproxPoly.jpg', cv.IMREAD_GRAYSCALE)
            m2 = cv.matchShapes(imgIdealPoly, imgApproxPoly, cv.CONTOURS_MATCH_I2, 0)
            comparisonPolyRounded = round(m2, 4)
    
            if comparisonPolyRounded > 0.1:
                return 'décalé'
            else :
                return 'entier'
            
    
    print(classifier(contours2))
    
    cv.waitKey(0)
    cv.destroyAllWindows()
    return classifier(contours2)
    
    
