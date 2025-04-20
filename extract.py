'''
1. color segmentation: separate the fabric from background
    color threshold for just the white fabric
    find the outer edges... how? -- > turns out there's a contour flag for this!
    or look for lines that are not contained by any combination of the other lines
    using canny, but that assumes rectangle fabric.
2. color segmentation: separate the cutout from the fabric
    easy, just thresholding. get a binary mask of the fabric.
4. scale using nickel for reference.
    i guess combined color and circle detection? can do basic color thresholding for now
5. determine the remaining area of the fabric. with scale this should be somewhat
    straightforward i think? can use a pixels-to-inches sort of thing
5. use some sort of packing algorithm on the leftover fabric? or even just
    cleave out the vertical strip with the cutout, like based on leftmost/rightmost
    points on cutout. (bounding box, basically.)
'''

import cv2 as cv
import numpy as np

DIR="images/"
FILE="example.png"
COIN_DIAMETER = 21.21 # currently, nickel diameter

raw_img = cv.imread(f'{DIR}{FILE}')
grey_img = cv.cvtColor(raw_img, cv.COLOR_BGR2GRAY)

# obtain pixel to millimeter ratio based on size of coin.
blurred_grey_img = cv.GaussianBlur(grey_img, (7, 7), 0) # blur to normalize coin color a bit
circles = cv.HoughCircles(blurred_grey_img, cv.HOUGH_GRADIENT, minDist=50,
                        dp=1.0, param1=100, param2=30,
                        minRadius=10, maxRadius=50)
coin = circles[0][0]
coin_radius_px = coin[2]
pix_to_mm = COIN_DIAMETER / (2 * coin_radius_px)

# otsu binary thresholding to isolate fabric from background.
# TODO: assumes background darker than fabric
thresh_val, binary_img = cv.threshold(grey_img,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
cv.circle(binary_img, (int(coin[0]), int(coin[1])), int(coin[2]) + 5, 255, -1) # mask coin

# remove pepper from image (likely due to the coin)
kernel = np.ones((5, 5), dtype=np.uint8)
smoothed_binary_img = cv.erode(cv.dilate(binary_img, kernel), kernel) 

# detect edges
contours, _ = cv.findContours(smoothed_binary_img, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

# cv.imshow("binary", binary_img)
# cv.waitKey(0)
# print(contours)
# cv.drawContours(raw_img, contours, -1, (0,255,0), 3)
# cv.imshow("circles", raw_img)
# cv.waitKey(0)