import time
from queue import Queue
from threading import Thread, Lock
import cv2
import sys
import os

from yolo4 import plateRecognition
from checkplates import check_license_plate

def log(msg):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)

def main():
    #log("\nStarting parking recognition service...")
    #time.sleep(2)
    cap = cv2.VideoCapture(0)
    
    sys.stdin = os.fdopen(sys.stdin.fileno(), 'r', 1)  # Line-buffered
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1) # Line-buffered
    
    try:
        sys.stderr.flush()
        sys.stdout.flush()
        
        while True:
            line = sys.stdin.readline()  # Read from stdin (piped input)
            
            if not line: #Verific daca am inchis pipe, adica nu am mai putut citi din el
                break # Ieșim din buclă

            line = line.rstrip('\n') # Elimină doar newline-ul de la sfârșit
            
            if line == "exit":
                break
            
            if line == "left":
                #print("EXEC LEFT");
                #do something
                plateNumber = plateRecognition(cap, "left")
                result = check_license_plate(plateNumber)
                print("\n")
                print(result)  # Only prints True/False
                sys.stdout.flush()
            elif line == 'right':
                #print("EXEC RIGHT")
                #do something
                plateNumber = plateRecognition(cap, "right")
                result = check_license_plate(plateNumber)
                print("\n")
                print(result)  # Only prints True/False
                sys.stdout.flush()
                
    except KeyboardInterrupt:
        print("\nScript stopped by user.")
    
main()