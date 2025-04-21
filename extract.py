import cv2 as cv
import numpy as np
import csv

DIR="images/"
SRC_FILE="example.png"
CSV_FILE="example_dims.csv"
PNG_CUTOUT="example_fabric_cutout.png"
PNG_BOXES="example_boxes_cutout.png"
COIN_DIAMETER = 21.21 # currently, nickel diameter

raw_img = cv.imread(f'{DIR}{SRC_FILE}')
grey_img = cv.cvtColor(raw_img, cv.COLOR_BGR2GRAY)

def save_to_png(fname, mask):
    white_space = np.full((mask.shape[0], mask.shape[1], 3), 255, dtype=np.uint8)
    fabric_cutout_im = cv.merge((white_space, mask)) # passing in the binary mask as alpha value
    cv.imwrite(fname, fabric_cutout_im)

# obtain pixel to millimeter ratio based on size of coin.
blurred_grey_img = cv.GaussianBlur(grey_img, (7, 7), 0) # blur to normalize coin color a bit
circles = cv.HoughCircles(blurred_grey_img, cv.HOUGH_GRADIENT, minDist=50,
                        dp=1.0, param1=100, param2=30,
                        minRadius=10, maxRadius=50)
coin = circles[0][0]
coin_radius_px = coin[2]
pix_to_mm = COIN_DIAMETER / (2 * coin_radius_px)

# otsu binary thresholding to isolate fabric from background.
thresh_val, binary_img = cv.threshold(grey_img,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
# heuristic: assume the largest region in the image is the fabric
white_count = np.count_nonzero(binary_img == 255)
black_count = np.count_nonzero(binary_img == 0)
if ( black_count > white_count ):
    binary_img = cv.bitwise_not(binary_img)

cv.circle(binary_img, (int(coin[0]), int(coin[1])), int(coin[2]) + 5, 255, -1) # mask coin

# remove pepper from image (likely due to the coin)
kernel = np.ones((5, 5), dtype=np.uint8)
smoothed_binary_img = cv.erode(cv.dilate(binary_img, kernel), kernel) 

# save out as png with only the fabric
save_to_png(f"{DIR}/{PNG_CUTOUT}", smoothed_binary_img)

# figure out the fabric boundaries: assume it's the largest white space in the binary image
contours, hierarchy = cv.findContours(smoothed_binary_img, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
areas = [cv.contourArea(c) for c in contours]
fabric_index = np.argmax(areas)

# get the minimum-area rectangle for each cutout within the fabric and fill it in as black (unavailable).
cutout_boxes_removed_img = smoothed_binary_img.copy()
cutout_contours = [ contours[i] for i, h in enumerate(hierarchy[0]) if h[3] == fabric_index ]
cutout_bounding_boxes = []
for cutout in cutout_contours:
    box_pts = np.round(cv.boxPoints(cv.minAreaRect(cutout))).astype(np.int32)
    cutout_bounding_boxes.append([box_pts[0], box_pts[1], box_pts[2], box_pts[3]])
    cv.drawContours(cutout_boxes_removed_img, [box_pts], 0, 0, thickness=-1)

save_to_png(f"{DIR}/{PNG_BOXES}", cutout_boxes_removed_img)

# compute measurement information for the fabric
fabric_rect = cv.minAreaRect(contours[fabric_index])
(fx, fy), (fw, fh), fangle = fabric_rect
fwidth, fheight = fw * pix_to_mm, fh * pix_to_mm
total_fabric_px = np.count_nonzero(smoothed_binary_img == 255)
total_fabric_area = total_fabric_px * (pix_to_mm ** 2)
usable_fabric_px = np.count_nonzero(cutout_boxes_removed_img == 255)
usable_fabric_area = usable_fabric_px * (pix_to_mm ** 2)

# save measurement information out to a csv! all measurements in mm / mm^2 or degrees
with open(f"{DIR}/{PNG_BOXES}", "w", newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["fabric_width", "fabric_height", "fabric_rotation_angle", "remaining_area", "usable_area"])
    writer.writerow([fwidth, fheight, fangle, total_fabric_area, usable_fabric_area])
    writer.writerow([])

    writer.writerow(["cutout_index", "centerpt_x", "centerpt_y", "width", "height", "rotation_angle"])
    for i, cutout in enumerate(cutout_contours):
        (cx, cy), (w, h), angle = cv.minAreaRect(cutout)
        center_x, center_y = cx * pix_to_mm, cy * pix_to_mm
        width, height = w * pix_to_mm, h * pix_to_mm
        writer.writerow([i, center_x, center_y, width, height, angle])