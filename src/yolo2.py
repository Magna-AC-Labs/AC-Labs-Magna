import torch
from PIL import Image
from torchvision import transforms as T
from collections import Counter
import os
from ultralytics import YOLO
import cv2

def plateRecognition():
    # Incarca modelul YOLO
    yolo_model = YOLO("/Users/mariusfiat/Programming_Environment/Magna/AC-Labs-Magna/ModelWeights/best.pt")

    # Incarca PARSeq OCR
    ocr_model = torch.hub.load('baudm/parseq', 'parseq_tiny', pretrained=True, trust_repo=True).eval()

    # Preprocesare imagine pentru PARSeq
    preprocess = T.Compose([
        T.Resize((32, 128), T.InterpolationMode.BICUBIC),
        T.ToTensor(),
        T.Normalize(0.5, 0.5)
    ])

    # Setup pentru detectie si salvare placute
    output_folder = "plates"
    os.makedirs(output_folder, exist_ok=True)
    cap = cv2.VideoCapture(0)

    count = 1
    MAX_SAVED = 30
    results_plates = []

    def clean_text(text):
        return ''.join(c for c in text.upper() if c.isalnum())

    while True:
        ret, frame = cap.read()
        if not ret or count > MAX_SAVED:
            break

        results = yolo_model(frame)[0]

        for box in results.boxes:
            conf = float(box.conf[0])
            if conf > 0.4:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cropped_plate = frame[y1:y2, x1:x2]
                filename = f"{output_folder}/plate_{count}.jpg"
                cv2.imwrite(filename, cropped_plate)
                print(f"[INFO] Salvat: {filename}")
                count += 1

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, "plate", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                if count > MAX_SAVED:
                    break

        cv2.imshow("Live YOLOv8 Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q') or count > MAX_SAVED:
            break

    cap.release()
    cv2.destroyAllWindows()

    # OCR pe toate imaginile din folder
    for filename in os.listdir(output_folder):
        if filename.lower().endswith(".jpg"):
            path = os.path.join(output_folder, filename)
            img = Image.open(path).convert('RGB')
            img_tensor = preprocess(img).unsqueeze(0)

            with torch.no_grad():
                pred = ocr_model(img_tensor).softmax(-1)
                label, _ = ocr_model.tokenizer.decode(pred)

            cleaned = clean_text(label[0])
            results_plates.append(cleaned)
            print(f"[OCR] {filename} : {cleaned}")

    # Vot majoritar
    counter = Counter(results_plates)
    most_common = counter.most_common(1)[0] if counter else ("N/A", 0)

    print("\n Rezultate finale OCR:")
    for text, count in counter.most_common():
        print(f"'{text}': {count} aparitii")

    print(f"\n Rezultatul cel mai frecvent: '{most_common[0]}' cu {most_common[1]} aparitii.")
    
    return most_common[0]