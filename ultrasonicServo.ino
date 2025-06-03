#include <Servo.h>

// Pin definitions
#define ECHO1ENTER_PIN 9 
#define TRIG1ENTER_PIN 8
#define ECHO2ENTER_PIN 7 
#define TRIG2ENTER_PIN 6

#define ECHO1LEAVE_PIN 5 
#define TRIG1LEAVE_PIN 4
#define ECHO2LEAVE_PIN 3 
#define TRIG2LEAVE_PIN 2

#define SERVOENTER_PIN 11
#define SERVOLEAVE_PIN 10

Servo barrierServoEnter;
Servo barrierServoLeave;

enum State { IDLE, WAIT_ACCESS, BARRIER_OPEN };

State enterState = IDLE;
State leaveState = IDLE;

unsigned long enterOpenTime = 0;
unsigned long leaveOpenTime = 0;

// Buffer rezultat pentru fiecare bariera
char serialEntryResult = 0;
char serialLeaveResult = 0;

void setup() {
  Serial.begin(9600);

  pinMode(ECHO1ENTER_PIN, INPUT);
  pinMode(TRIG1ENTER_PIN, OUTPUT);
  pinMode(ECHO2ENTER_PIN, INPUT);
  pinMode(TRIG2ENTER_PIN, OUTPUT);

  pinMode(ECHO1LEAVE_PIN, INPUT);
  pinMode(TRIG1LEAVE_PIN, OUTPUT);
  pinMode(ECHO2LEAVE_PIN, INPUT);
  pinMode(TRIG2LEAVE_PIN, OUTPUT);

  barrierServoEnter.attach(SERVOENTER_PIN);
  barrierServoLeave.attach(SERVOLEAVE_PIN);
  
  barrierServoEnter.write(0);
  barrierServoLeave.write(0);
}

void loop() {
  long distance1Enter = readUltrasonic(ECHO1ENTER_PIN, TRIG1ENTER_PIN);
  long distance2Enter = readUltrasonic(ECHO2ENTER_PIN, TRIG2ENTER_PIN);
  long distance1Leave = readUltrasonic(ECHO1LEAVE_PIN, TRIG1LEAVE_PIN);
  long distance2Leave = readUltrasonic(ECHO2LEAVE_PIN, TRIG2LEAVE_PIN);

  while (Serial.available()) {
    char c = Serial.read();
    if (c == 'A' || c == 'B') serialEntryResult = c;
    if (c == 'C' || c == 'D') serialLeaveResult = c;
  }

  handleEntryBarrier(distance1Enter, distance2Enter);
  handleLeaveBarrier(distance1Leave, distance2Leave);

  delay(50); // Pentru debounce
}

void handleEntryBarrier(long dist1, long dist2) {
  switch (enterState) {
    case IDLE:
      if (dist1 > 0 && dist1 < 30) {
        serialEntryResult = 0; // Sterge vechiul raspuns
        Serial.println("TRIGGER_ENTER");
        enterState = WAIT_ACCESS;
      }
      break;
    case WAIT_ACCESS:
      if (serialEntryResult) {
        if (serialEntryResult == 'A') {
          barrierServoEnter.write(90);
          enterOpenTime = millis();
          enterState = BARRIER_OPEN;
        } else if (serialEntryResult == 'B') {
          denyEntry();
          enterState = IDLE;
        }
        serialEntryResult = 0;
      }
      break;
    case BARRIER_OPEN:
      if (millis() - enterOpenTime > 3000) {
        if (dist2 > 0 && dist2 < 30) {
        } else {
          barrierServoEnter.write(0);
          enterState = IDLE;
        }
      }
      break;
  }
}

void handleLeaveBarrier(long dist1, long dist2) {
  switch (leaveState) {
    case IDLE:
      if (dist1 > 0 && dist1 < 30) {
        serialLeaveResult = 0;
        Serial.println("TRIGGER_LEAVE");
        leaveState = WAIT_ACCESS;
      }
      break;
    case WAIT_ACCESS:
      if (serialLeaveResult) {
        if (serialLeaveResult == 'C') {
          barrierServoLeave.write(90);
          leaveOpenTime = millis();
          leaveState = BARRIER_OPEN;
        } else if (serialLeaveResult == 'D') {
          denyLeave();
          leaveState = IDLE;
        }
        serialLeaveResult = 0;
      }
      break;
    case BARRIER_OPEN:
      if (millis() - leaveOpenTime > 3000) {
        if (dist2 > 0 && dist2 < 30) {
        } else {
          barrierServoLeave.write(0);
          leaveState = IDLE;
        }
      }
      break;
    default:
      leaveState = IDLE;
      break;
  }
}

void denyEntry() {
  for (int i = 0; i < 2; i++) {
    barrierServoEnter.write(45);
    delay(150);
    barrierServoEnter.write(0);
    delay(150);
  }
}

void denyLeave() {
  for (int i = 0; i < 2; i++) {
    barrierServoLeave.write(45);
    delay(150);
    barrierServoLeave.write(0);
    delay(150);
  }
}


long readUltrasonic(int echoPin, int trigPin) {
  digitalWrite(trigPin, LOW); delayMicroseconds(2);
  digitalWrite(trigPin, HIGH); delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH, 20000);
  if (duration == 0) return -1;
  long distance = duration / 58;
  return distance;
}
