import cv2
import imutils
import numpy as np
import pytesseract
import subprocess
from checkplates import check_license_plate

# ======= Utility Functions ========

def capture_photo(path='photo.jpg'):
    print("Capturing image...")
    subprocess.run(['libcamera-jpeg', '-o', path, '-t', '2000'], check=True)
    print("Image captured.")

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
    return cv2.warpPerspective(image, M, (maxWidth, maxHeight))

def unsharp_mask(image, kernel_size=(5, 5), sigma=1.0, amount=1.5, threshold=0):
    blurred = cv2.GaussianBlur(image, kernel_size, sigma)
    sharpened = float(amount + 1) * image - float(amount) * blurred
    sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
    if threshold > 0:
        low_contrast_mask = np.abs(image - blurred) < threshold
        np.copyto(sharpened, image, where=low_contrast_mask)
    return sharpened

# ============ Main Function ============

def detect_license_plate(image_path='photo.jpg'):
    img = cv2.imread(image_path)
    if img is None:
        print("Error: Image not found.")
        return

    img = cv2.resize(img, (620, 480))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    gray = unsharp_mask(gray)

    edged = cv2.Canny(gray, 30, 200)
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
        print("No license plate detected.")
        return

    warped = four_point_transform(img, screenCnt.reshape(4, 2))
    gray_plate = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    gray_plate = unsharp_mask(gray_plate)
    _, plate_thresh = cv2.threshold(gray_plate, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    config = '--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    text = pytesseract.image_to_string(plate_thresh, config=config)
    plate = text.strip().upper().replace(" ", "")

    print(f"\nDetected Plate: {plate}")

    if check_license_plate(plate):
        print("Permission Granted (valid plate)")
    else:
        print("Permission Denied (invalid plate)")

# ============ Entry Point ============

if __name__ == "__main__":
    capture_photo()
    detect_license_plate()
