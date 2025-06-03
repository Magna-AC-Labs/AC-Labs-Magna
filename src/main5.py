import serial
import time
from queue import Queue
from threading import Thread, Lock
import cv2

from yolo4 import plateRecognition
from checkplates import check_license_plate

SERIAL_PORT = 'COM8'
BAUDRATE = 9600

camera_lock = Lock()
serial_lock = Lock()

def log(msg):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def process_queue(queue, cap, side, ser):
    while True:
        trigger = queue.get()
        if trigger is None:
            break
        log(f"Procesare {side} triggered!")

        with camera_lock:
            plate_number = plateRecognition(cap, side)
        log(f"[{side}] Detected plate: {plate_number}")

        allowed = check_license_plate(plate_number)
        log(f"[{side}] Access {'GRANTED' if allowed else 'DENIED'} for plate {plate_number}")

        with serial_lock:
            if side == 'left':
                ser.write(b'A' if allowed else b'B')
                log(f"[{side}] Sent '{'A' if allowed else 'B'}' to Arduino.")
            else:
                ser.write(b'C' if allowed else b'D')
                log(f"[{side}] Sent '{'C' if allowed else 'D'}' to Arduino.")
        queue.task_done()

def main():
    log("Starting parking recognition service...")
    ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
    time.sleep(2)
    cap = cv2.VideoCapture(0)

    queue_left = Queue()
    queue_right = Queue()

    t_left = Thread(target=process_queue, args=(queue_left, cap, 'left', ser), daemon=True)
    t_right = Thread(target=process_queue, args=(queue_right, cap, 'right', ser), daemon=True)
    t_left.start()
    t_right.start()

    log(f"Listening for trigger on {SERIAL_PORT} at {BAUDRATE} baud.")

    try:
        while True:
            line = ser.readline().decode(errors='ignore').strip()
            if not line:
                continue
            log(f"Received: '{line}'")
            if line.upper() == 'TRIGGER_ENTER':
                queue_left.put(True)
            elif line.upper() == 'TRIGGER_LEAVE':
                queue_right.put(True)
    except KeyboardInterrupt:
        log("Shutting down...")
    finally:
        queue_left.put(None)
        queue_right.put(None)
        t_left.join()
        t_right.join()
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
