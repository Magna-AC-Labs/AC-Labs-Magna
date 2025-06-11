#ifndef __SERIAL_H
#define __SERIAL_H

void Serial_Init(char*);
void Serial_Transmit(char[]);
char* Serial_Receive(void);
void Serial_ClosePort(void);

#endif