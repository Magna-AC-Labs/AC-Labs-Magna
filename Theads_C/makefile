compile:
	gcc -g -Wall -c serial.c
	gcc -g -Wall -c main.c

build: compile
	gcc -g -Wall -o exec main.o serial.o

buildRapid:
	gcc -g -Wall -o exec main2_RAPID.c serial.c

run:
	./exec

clean:
	rm *.o exec