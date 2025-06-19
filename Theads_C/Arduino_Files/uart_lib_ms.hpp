#ifndef __URART_LIB_MS
#define __URART_LIB_MS

void USART_Init(void); //Baud Rate 115200
void USART_Transmit_CH(unsigned char ch);
void USART_Transmit_STRING(unsigned char *string);
unsigned char USART_Receive(void);
bool USART_Available();

#endif