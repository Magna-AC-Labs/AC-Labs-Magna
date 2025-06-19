#include <avr/io.h>
#include <string.h>

#include "uart_lib_ms.hpp"

void USART_Init(void){
    //* Pin directions
    DDRD &= ~(1<<PD0); //* RxD input
    DDRD |= (1<<PD1);  //* TxD output

    //* Select Asynchronous USART mode
    UCSR0C &= ~(1 << UMSEL01);
    UCSR0C &= ~(1 << UMSEL00);

    //* No parity
    UCSR0C &= ~(1 << UPM01);
    UCSR0C &= ~(1 << UPM00);

    //* One stop bit
    UCSR0C &= ~(1 << USBS0);

    //* 8 bits of data
    UCSR0B &= ~(1 << UCSZ02);
    UCSR0C |= (1 << UCSZ01) | (1 << UCSZ00);

    //* Baud rate 9600 = 103 for 16MHZ
    //* Baud rate 115200 = 8
    UBRR0L = 103;

    //* Enable TXC RXC
    UCSR0B |= (1 << RXEN0) | (1 << TXEN0);
}

void USART_Transmit_CH(unsigned char data){
    /* Wait for empty transmit buffer */
    while(!(UCSR0A & (1 << UDRE0)));
    UDR0 = data;
}

unsigned char USART_Receive(void){
    /* Wait for data to be received */
    while(!(UCSR0A & (1 << RXC0)));

    /* Get and return received data from buffer */
    return UDR0;
}

void USART_Transmit_STRING(unsigned char* string){
    for(int i = 0; i < strlen(string); i++){
        USART_Transmit_CH(string[i]);
    }
}

bool USART_Available(){
    if(UCSR0A & (1 << RXC0)){
        return true;
    }
    return false;
}