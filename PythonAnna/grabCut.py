import numpy as np
import cv2 as cv
#from matplotlib import pyplot as plt

# the aim: extract the image of interest (one oreo), then draw its contours

img = cv.imread('mange2.jpg')
assert img is not None, "file could not be read"
mask = np.zeros(img.shape[:2],np.uint8)
bgdModel = np.zeros((1,65),np.float64)
fgdModel = np.zeros((1,65),np.float64)
# rect dimensions for 'mange': 440, 380, 510, 450
# rect dimensions for 'entier2', 'fissure': 345, 237, 510, 450
# rect dimensions for 'entier1': 645, 237, 510, 450
# rect dimensions for 'entier3': 645, 237, 510, 450
# rect dimensions for 'fissure2': 545, 207, 510, 450 !!!
# rect dimensions for 'fissure3': 445, 97, 510, 450 
# rect dimensions for 'fissure4': 445, 97, 510, 450 

rect = (440, 217, 510, 450)
cv.grabCut(img,mask,rect,bgdModel,fgdModel,5,cv.GC_INIT_WITH_RECT)
mask2 = np.where((mask==2)|(mask==0),0,1).astype('uint8')
img = img*mask2[:,:,np.newaxis]

cv.imwrite('image.jpg',img)
modImg = cv.imread('image.jpg', cv.IMREAD_GRAYSCALE)  
thresh, BW = cv.threshold(modImg,50,255,cv.THRESH_BINARY + cv.THRESH_OTSU)
contours, hierarchy = cv.findContours(BW,  cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
temp = np.zeros((modImg.shape[0],modImg.shape[1],3), dtype = np.uint8)
cv.drawContours(temp,contours, -1,(0,0,255),1)
#cv.imshow('Original Image',img)

kernel = cv.getStructuringElement(cv.MORPH_RECT,(5,5))
dilated = cv.dilate(modImg, kernel)
contours, _ = cv.findContours(dilated.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

# finding ideal circle
modImg = cv.medianBlur(modImg,5)
cimg = cv.cvtColor(modImg,cv.COLOR_GRAY2BGR)
circles = cv.HoughCircles(modImg, cv.HOUGH_GRADIENT, 1.2, 1000)
print('circle area:', 3.14*(circles[0][0][2]**2))

print('contour\'s area:', cv.contourArea(contours[0]))
cv.imshow('Contours Drawn',temp)
cv.waitKey(0)
cv.destroyAllWindows()

#plt.imshow(img),plt.colorbar(),plt.show()