
import cv2

def main():

    im1 = cv2.imread("img/entier1.png",cv2.IMREAD_GRAYSCALE)
    im11 = cv2.imread("img/entier2.png",cv2.IMREAD_GRAYSCALE)
    im2 = cv2.imread("img/mange.png",cv2.IMREAD_GRAYSCALE)
    im3 = cv2.imread("img/fissure.png",cv2.IMREAD_GRAYSCALE)
    im4 = cv2.imread("img/ciseaux.png",cv2.IMREAD_GRAYSCALE)
    im5 = cv2.imread("img/entier3.png",cv2.IMREAD_GRAYSCALE)
    im6 = cv2.imread("img/entier202.png",cv2.IMREAD_GRAYSCALE)

    m1 = cv2.matchShapes(im1,im1,cv2.CONTOURS_MATCH_I2,0)
    m11 = cv2.matchShapes(im1,im11,cv2.CONTOURS_MATCH_I2,0)
    m111 = cv2.matchShapes(im11,im2,cv2.CONTOURS_MATCH_I2,0)
    m2 = cv2.matchShapes(im1,im2,cv2.CONTOURS_MATCH_I2,0)
    m22 = cv2.matchShapes(im1,im3,cv2.CONTOURS_MATCH_I2,0)
    m222 = cv2.matchShapes(im11,im3,cv2.CONTOURS_MATCH_I2,0)
    m3 = cv2.matchShapes(im1,im4,cv2.CONTOURS_MATCH_I2,0)
    m33 = cv2.matchShapes(im11,im4,cv2.CONTOURS_MATCH_I2,0)

    # comparisons with entier3
    m4 = cv2.matchShapes(im1,im5,cv2.CONTOURS_MATCH_I2,0)
    m5 = cv2.matchShapes(im11,im5,cv2.CONTOURS_MATCH_I2,0)
    m6 = cv2.matchShapes(im5,im2,cv2.CONTOURS_MATCH_I2,0)
    m7 = cv2.matchShapes(im5,im3,cv2.CONTOURS_MATCH_I2,0)
    m8 = cv2.matchShapes(im5,im4,cv2.CONTOURS_MATCH_I2,0)

    # entier2 vs entier 202
    m9 = cv2.matchShapes(im11,im6,cv2.CONTOURS_MATCH_I2,0)


    print("\n------------------------- \nMatchShapes pour entier1 et entier2 \n-------------------------")

    print("entier1.png et entier1.png : {}".format(m1))
    print("entier1.png et entier2.png : {}".format(m11))
    print("entier1.png et mange.png : {}".format(m2))
    print("entier2.png et mange.png : {}".format(m111))
    print("entier1.png et fissure.png : {}".format(m22))
    print("entier2.png et fissure.png : {}".format(m222))
    print("entier1.png et ciseaux.png : {}".format(m3))
    print("entier2.png et ciseaux.png : {}".format(m33))
    print("entier2.png et entier202.png : {}".format(m9))

    # prints for entier3
    print("\n------------------------- \nMatchShapes pour entier3 \n-------------------------")
    print("entier1.png et entier3.png : {}".format(m4))
    print("entier2.png et entier3.png : {}".format(m5))
    print("entier3.png et mange.png : {}".format(m6))
    print("entier3.png et fissure.png : {}".format(m7))
    print("entier3.png et ciseaux.png : {}".format(m8))

if __name__ == "__main__":
    main()