#include <avr/io.h>
#include "uart_lib_ms.hpp"
#include <Servo.h>

Servo myservo;

void Servo_Init(Servo servo){
  servo.write(0);
}

void setup() {
  // put your setup code here, to run once:
  USART_Init();     // Dau init la usart programat prin registrii
  pinMode(13, OUTPUT);  //Ledul integrat
  myservo.attach(9); 
  Servo_Init(myservo);
}

void loop() {
  // put your main code here, to run repeatedly:
  unsigned char data = USART_Receive();

  if(data == 'A'){
    digitalWrite(13, HIGH);
    for(int i = 0; i < 70; i++){
      myservo.write(i);
      _delay_ms(5);
    }
  }
  else if(data == 'B'){
    digitalWrite(13, LOW);
    for(int i = 70; i >= 0; i--){
      myservo.write(i);
      _delay_ms(5);
    }
  }
  _delay_ms(1000);
}
