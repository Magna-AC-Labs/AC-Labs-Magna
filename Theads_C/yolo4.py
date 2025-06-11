import torch
from PIL import Image
from torchvision import transforms as T
from collections import Counter
from ultralytics import YOLO
import cv2
import time

YOLO_PATH = "/Users/mariusfiat/Programming_Environment/Magna/AC-Labs-Magna/ModelWeights/best.pt"
MAX_SAVED = 5

# Încarcă modelul YOLO și PARSeq
yolo_model = YOLO(YOLO_PATH)
ocr_model = torch.hub.load('baudm/parseq', 'parseq_tiny', pretrained=True, trust_repo=True).eval()

def preprocess_img(img):
    preprocess = T.Compose([
        T.Resize((32, 128), T.InterpolationMode.BICUBIC),
        T.ToTensor(),
        T.Normalize(0.5, 0.5)
    ])
    return preprocess(img).unsqueeze(0)

def ocr_plate(cropped_plate):
    img = Image.fromarray(cv2.cvtColor(cropped_plate, cv2.COLOR_BGR2RGB))
    img_tensor = preprocess_img(img)
    with torch.no_grad():
        pred = ocr_model(img_tensor).softmax(-1)
        label, _ = ocr_model.tokenizer.decode(pred)
    cleaned = ''.join(c for c in label[0].upper() if c.isalnum())
    return cleaned

def draw_detection(frame, x1, y1, x2, y2, text):
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    return frame

def get_roi(frame, side):
    H, W, _ = frame.shape
    if side == 'left':
        roi = frame[:, :W//2, :]
        offset = 0
    else:
        roi = frame[:, W//2:, :]
        offset = W // 2
    return roi, offset

def detect_plates(cap, side):
    results_plates = []
    num_detected = 0

    while num_detected < MAX_SAVED:
        ret, frame = cap.read()
        if not ret:
            break

        roi, offset = get_roi(frame, side)
        results = yolo_model(roi)[0]
        preview_frame = frame.copy()
        H, W, _ = preview_frame.shape

        for box in results.boxes:
            conf = float(box.conf[0])
            if conf > 0.4:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                x1 += offset
                x2 += offset
                cropped_plate = frame[y1:y2, x1:x2]
                text = ocr_plate(cropped_plate)
                results_plates.append(text)
                preview_frame = draw_detection(preview_frame, x1, y1, x2, y2, text)
                print(f"[OCR {side}] #{num_detected+1} : {text}")
                num_detected += 1
                break  # doar prima plăcuță găsită pe frame

        if side == 'left':
            show = preview_frame[:, :W // 2, :]
        else:
            show = preview_frame[:, W // 2:, :]
        #cv2.imshow(f"Live View {side}", show)

        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

        time.sleep(0.1)

    cv2.destroyAllWindows()
    return results_plates

def plateRecognition(cap, side):
    results_plates = detect_plates(cap, side)
    if results_plates:
        counter = Counter(results_plates)
        most_common = counter.most_common(1)[0]
        print(f"\nCel mai frecvent {side}: '{most_common[0]}' cu {most_common[1]} aparitii.")
        return most_common[0]
    else:
        print(f"\nNu s-a detectat nicio plăcuță pe {side}.")
        return "N/A"