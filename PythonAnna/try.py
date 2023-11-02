import cv2 
import numpy as np 
  
image = cv2.imread('img/entier3.jpg',1) 
# find canny edges 
edged = cv2.Canny(image, 30, 200) 
cv2.waitKey(0) 
  
# find contours 
contours, hierarchy = cv2.findContours(edged,  
    cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) 
cv2.imshow('Original', image) 
cv2.imshow('Canny Edges After Contouring', edged)  
  
cv2.drawContours(image, contours, -1, (0, 255, 0), 3) 
  
cv2.imshow('Contours', image) 
cv2.waitKey(0) 
cv2.destroyAllWindows() 