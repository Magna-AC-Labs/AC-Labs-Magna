import cv2
import imutils
import numpy as np
import pytesseract
import subprocess
from collections import Counter
from yolo2 import plateRecognition
from checkplates import check_license_plate
from carLicensePlateRecognition import checkPlate2
import serial
import time

#plateNumber = plateRecognition()
plateNumber = checkPlate2()
result = check_license_plate(plateNumber)
print(result)

ser = serial.Serial('/dev/cu.usbserial-AB0ONA10', 9600)
if result == True:
    time.sleep(2)
    ser.write(b'A')
    time.sleep(2)
    ser.write(b'B')
else:
    ser.write(b'B')

ser.close()