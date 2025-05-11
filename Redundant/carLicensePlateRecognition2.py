import cv2
import numpy as np
import pytesseract
import imutils
import logging

# Optional: Set Tesseract path (needed in some Raspberry Pi setups)
# pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

logging.basicConfig(level=logging.INFO)

def order_points(pts):
    """Orders 4 points for perspective transform."""
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]  # Top-left
    rect[2] = pts[np.argmax(s)]  # Bottom-right

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # Top-right
    rect[3] = pts[np.argmax(diff)]  # Bottom-left

    return rect

def four_point_transform(image, pts):
    """Applies perspective transform to get a top-down view."""
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
        [0, maxHeight - 1]], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    return warped

def preprocess_image(image_path):
    """Loads and preprocesses image."""
    image = cv2.imread(image_path)
    if image is None:
        logging.error("Image not found!")
        return None, None

    image = cv2.resize(image, (480, 360))  # Resize for speed
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    edged = cv2.Canny(gray, 30, 200)

    return image, edged

def find_plate_contour(edged):
    """Finds the most probable license plate contour."""
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]

    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.018 * peri, True)
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = w / float(h)
            if 2 < aspect_ratio < 5:
                return approx

    return None

def ocr_plate(warped):
    """Performs OCR on the transformed plate image."""
    gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Optional: Morphology to remove noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    config = '--oem 1 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    text = pytesseract.image_to_string(cleaned, config=config)
    return text.strip(), cleaned

def main(image_path):
    image, edged = preprocess_image(image_path)
    if image is None or edged is None:
        return

    plate_contour = find_plate_contour(edged)
    if plate_contour is None:
        logging.warning("No license plate contour found.")
        return

    warped = four_point_transform(image, plate_contour.reshape(4, 2))
    text, cleaned_plate = ocr_plate(warped)

    logging.info(f"Detected License Plate Text: {text}")

    # Save results instead of showing (good for headless Pi)
    cv2.imwrite("detected_plate.jpg", cleaned_plate)
    cv2.imwrite("edged.jpg", edged)
    logging.info("Saved plate image as 'detected_plate.jpg'")

# Run the pipeline
if __name__ == "__main__":
    main("photo1.jpg")
