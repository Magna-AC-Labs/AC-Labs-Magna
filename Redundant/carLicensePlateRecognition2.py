import cv2
import imutils
import numpy as np
import pytesseract
from PIL import Image

def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]     # top-left
    rect[2] = pts[np.argmax(s)]     # bottom-right
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # top-right
    rect[3] = pts[np.argmax(diff)]  # bottom-left
    return rect

def four_point_transform(image, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)

    maxWidth = max(int(widthA), int(widthB))
    maxHeight = max(int(heightA), int(heightB))

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    return warped

def unsharp_mask(image, kernel_size=(5, 5), sigma=1.0, amount=1.5, threshold=0):
    blurred = cv2.GaussianBlur(image, kernel_size, sigma)
    sharpened = float(amount + 1) * image - float(amount) * blurred
    sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
    if threshold > 0:
        low_contrast_mask = np.abs(image - blurred) < threshold
        np.copyto(sharpened, image, where=low_contrast_mask)
    return sharpened

# Read and resize input
img = cv2.imread('photo1.jpg')
if img is None:
    print("Eroare: imaginea nu a fost gasita.")
    exit()

img = cv2.resize(img, (620, 480))

# Preprocess image
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.bilateralFilter(gray, 11, 17, 17)

# Optional sharpening of full image (can improve contour detection)
gray = unsharp_mask(gray)

cv2.imshow("gray", gray)
cv2.waitKey(0)

# Edge detection
edged = cv2.Canny(gray, 30, 200)
cv2.imshow("edged", edged)
cv2.waitKey(0)

# Detect contours
cnts = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:10]
screenCnt = None

for c in cnts:
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.018 * peri, True)
    if len(approx) == 4:
        screenCnt = approx
        break

if screenCnt is None:
    print("No contour detected.")
    exit()

cv2.drawContours(img, [screenCnt], -1, (0, 255, 0), 3)
cv2.imshow("Contours", img)
cv2.waitKey(0)

# Perspective transform
warped = four_point_transform(img, screenCnt.reshape(4, 2))

# Convert to grayscale for OCR
gray_plate = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)

# Apply sharpening to plate region
gray_plate = unsharp_mask(gray_plate)

# Thresholding for OCR
_, plate_thresh = cv2.threshold(gray_plate, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

# OCR
config = '--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
text = pytesseract.image_to_string(plate_thresh, config=config, lang='eng')
print("Detected Number is:", text.strip())

# Show result
cv2.imshow("Original Image", img)
cv2.imshow("Cropped & Corrected Plate", plate_thresh)
cv2.waitKey(0)
cv2.destroyAllWindows()
