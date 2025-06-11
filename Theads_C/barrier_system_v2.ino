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

#define NUMAR_LOCURI 2
#define SERVO_DISTANCE 10

// #define RED_LED 
// #define GREEN_LED

Servo barrierServoEnter;
Servo barrierServoLeave;

enum State { IDLE, WAIT_ACCESS, BARRIER_OPEN };

State enterState = IDLE;
State leaveState = IDLE;

unsigned long enterOpenTime = 0;
unsigned long leaveOpenTime = 0;
int numarLocuri = NUMAR_LOCURI;

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

  char c, correct_ch;
  while(Serial.available()){
    correct_ch = Serial.read();
    if(isalpha(correct_ch) && correct_ch != EOF && correct_ch != '\n'){
      c = correct_ch;
      if (c == 'A' || c == 'B') serialEntryResult = c;
      if (c == 'C' || c == 'D') serialLeaveResult = c;
    }
  }

  handleEntryBarrier(distance1Enter, distance2Enter);
  handleLeaveBarrier(distance1Leave, distance2Leave);

  delay(50); // Pentru debounce
}

void handleEntryBarrier(long dist1, long dist2) {
  switch (enterState) {
    case IDLE:
      if (dist1 > 0 && dist1 < SERVO_DISTANCE) {
        serialEntryResult = 0; // Sterge vechiul raspuns
        if(numarLocuri == 0){
          Serial.println("N");
        }
        else{
          Serial.println("E");
          enterState = WAIT_ACCESS;
        }
      }
      break;
    case WAIT_ACCESS:
      if (serialEntryResult) {
        if (serialEntryResult == 'A' && numarLocuri > 0) {
          barrierServoEnter.write(90);
          enterOpenTime = millis();
          numarLocuri--;
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
        if (dist2 > 0 && dist2 < SERVO_DISTANCE) {
          enterOpenTime = millis();
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
      if (dist1 > 0 && dist1 < SERVO_DISTANCE) {
        serialLeaveResult = 0;
        Serial.println("L");
        leaveState = WAIT_ACCESS;
      }
      break;
    case WAIT_ACCESS:
      if (serialLeaveResult) {
        if (serialLeaveResult == 'C') {
          barrierServoLeave.write(90);
          leaveOpenTime = millis();
          numarLocuri++;
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
        if (dist2 > 0 && dist2 < SERVO_DISTANCE) {
          leaveOpenTime = millis();
        } else {
          barrierServoLeave.write(0);
          leaveState = IDLE;
        }
      }
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
    barrierServoLeave.write(20);
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
  long distance = duration / 58;
  return distance;
}
