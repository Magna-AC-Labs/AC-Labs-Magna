#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <pthread.h>
#include <time.h>
#include <unistd.h>     
#include <sys/wait.h> 

#include "serial.h"

#define SERIAL_PORT "/dev/cu.usbserial-AB0ONA10"
#define SCRIPT_PATH "/Users/mariusfiat/Programming_Environment/Magna/Theads_C/main_run.py"
#define PYTHON_INTERPRETER "/Users/mariusfiat/Programming_Environment/Magna/venv/bin/python3"
#define MAX_LINE_LENGTH 256 

//* Variables delaration
pthread_mutex_t serial_lock;
pthread_mutex_t queue_lock;
int pipe_C_Python[2]; // Pipe pentru C -> Python (C scrie, Python citește)
int pipe_Python_C[2]; // Pipe pentru Python -> C (Python scrie, C citește)
pid_t pid;

typedef struct{ //* Structura folosita pentru fiecare request de la arduino
    bool request;  //* Flag care se seteaza cand se face o cerere de intrare sau de iesire
    bool proccessed;  //* Flag care se seteaza daca comanda a fost procesata (numarul a fost captat si verificat) 
    bool result;    //* Flag care salveaza rezultatul salvarii si captarii, daca mi se permite sau nu intrarea in parcare
    bool blocked;   //* Nefolosit
}Request_t;

Request_t queue[2] = {{false, false, false, false}, {false, false, false, false}}; //* Pot avea maxim 100 cereri in coada.
/*
    queue[0] folosit pentru a genera cereri la intrare,
    queue[1] folosit pentru a genera cereri la iesire
*/

//* Functions declaration
void runPythonScript(const char* scriptPath);  //* Functia care ruleaza scriptul de python cu detectia si verificarea numarului 
void* read_Thread(void* args);    //* Functia pe care o executa threadul de comunicare pe interfata seriala dintre raspberry pi si arduino, primeste si trimte mesajele
void* generate_Func(void* args);  //* Functia pe care o executa threadul care porneste camera pentru verificare numar de inmatriculare
void printRequest(int);   //* 
void delay(int number_of_seconds);
void busy_delay_ms(long);

//*

int main() {
    //* Mutex care imi blocheaza accesul multiplu la interfata seriala
    pthread_mutex_init(&serial_lock, NULL);
    pthread_mutex_init(&queue_lock, NULL);

    //* Ambele threaduri au acces la interfata seriala dar o sa folosesc mutex ca sa nu am accesari in acelasi timp
    Serial_Init(SERIAL_PORT); //* Initializez si setez toti parametrii

    //* Creez thredurile
    pthread_t serial_Thread, generate_Thread;

    pthread_create(&serial_Thread, NULL, read_Thread, NULL);
    pthread_create(&generate_Thread, NULL, generate_Func, NULL);

    //* Astept sa se termine threadurile
    pthread_join(serial_Thread, NULL);
    pthread_join(generate_Thread, NULL);

    Serial_ClosePort();
    pthread_mutex_destroy(&serial_lock);
    pthread_mutex_destroy(&queue_lock);
    return 0; // success
};

void runPythonScript(const char* scriptPath){ //* Alternativa pentru metoda cu creare pipe, fork, procesul copil face exec pe calea scriptului, 
//* [...] redirectarea iesirii scriptului care scrie in pipe si procesul parinte citeste rezultatul din pipe.
    printf("Python script running... \n");

    // Creează pipe-ul C -> Python
    if (pipe(pipe_C_Python) == -1) {
        perror("Eroare la crearea pipe-ului C_Python");
        exit(EXIT_FAILURE);
    }

    // Creează pipe-ul Python -> C
    if (pipe(pipe_Python_C) == -1) {
        perror("Eroare la crearea pipe-ului Python_C");
        exit(EXIT_FAILURE);
    }

    pid = fork(); // Creează procesul copil

    if (pid == -1) {
        perror("Eroare la fork");
        exit(EXIT_FAILURE);
    }

    if (pid == 0) { // Procesul copil (Python)
        // Închide capetele pipe-urilor pe care nu le folosește copilul
        close(pipe_C_Python[1]); // Copilul nu scrie în pipe-ul C_Python
        close(pipe_Python_C[0]); // Copilul nu citește din pipe-ul Python_C

        // Redirecționează stdin (0) al copilului către capătul de citire al pipe-ului C_Python
        if (dup2(pipe_C_Python[0], 0) == -1) {
            perror("Eroare dup2 pipe_C_Python[0]");
            exit(EXIT_FAILURE);
        }
        // Redirecționează stdout (1) al copilului către capătul de scriere al pipe-ului Python_C
        if (dup2(pipe_Python_C[1], 1) == -1) {
            perror("Eroare dup2 pipe_Python_C[1]");
            exit(EXIT_FAILURE);
        }

        // Închide descriptorii originali după dup2
        close(pipe_C_Python[0]);
        close(pipe_Python_C[1]);

        // Execută scriptul Python
        execl(PYTHON_INTERPRETER, "python3", SCRIPT_PATH, NULL);
        //execl("/bin/sh", "sh", "-c", "python3 /Users/mariusfiat/Programming_Environment/Magna/Theads_C/main_run.py | grep -E 'True|False'", NULL);

        // Dacă execl eșuează, se va ajunge aici
        perror("Eroare la execl (verifică calea interpreterului Python sau a scriptului)");
        exit(EXIT_FAILURE);
    }
}

void* read_Thread(void* args){
    char msg[10];
    bool proccessed_E, proccessed_L;
    bool result_E, result_L;
    
    while(1){
        pthread_mutex_lock(&serial_lock);
            strcpy(msg, Serial_Receive()); //* Citesc de pe interfata seriala, mesaje de la arduino 
        pthread_mutex_unlock(&serial_lock);

        if(strlen(msg) != 0){ //* Daca am citit ceva valid, inseamna ca e un request
            pthread_mutex_lock(&queue_lock);
            if(strcmp(msg, "E") == 0 && queue[0].request == false){
                printf("Am primit pe intrare %s\n", msg);
                queue[0].request = true;
            } else if(strcmp(msg, "L") == 0 && queue[1].request == false){
                printf("Am primit pe iesire %s\n", msg);
                queue[1].request = true;
            } else if(strcmp(msg, "N") == 0 && queue[0].request == false){
                printf("Numar insuficient de locuri!\n");
                queue[0].request = false;
            }
            pthread_mutex_unlock(&queue_lock);
        } 
        else{
            pthread_mutex_lock(&queue_lock);
            proccessed_E = queue[0].proccessed;
            result_E = queue[0].result;
            proccessed_L = queue[1].proccessed;
            result_L = queue[1].result;
            pthread_mutex_unlock(&queue_lock);

            if(proccessed_E == true){
                if(result_E == true){
                    //* Deschid intrarea
                    printf("Deschid intrarea\n");
                    strcpy(msg, "A");   //* Am primit accesul sa ridic bariera
                    Serial_Transmit(msg);
                }
                else if(result_E == false){
                    printf("Intrarea ramane inchisa\n");
                    strcpy(msg, "B");
                    Serial_Transmit(msg);
                }

                pthread_mutex_lock(&queue_lock);
                queue[0].request = false; //* Am procesat requestul si acum dau clear
                queue[0].proccessed = false;
                pthread_mutex_unlock(&queue_lock);
            }
            
            if(proccessed_L == true){
                if(result_L == true){
                    //* Deschid iesirea
                    printf("Deschid iesirea\n");
                    strcpy(msg, "C"); 
                    Serial_Transmit(msg);
                } else if(result_L == false){
                    printf("Iesirea ramane inchisa\n");
                    strcpy(msg, "D");
                    Serial_Transmit(msg);
                }
                pthread_mutex_lock(&queue_lock);
                queue[1].request = false; //* Am procesat requestul si acum dau clear
                queue[1].proccessed = false;
                pthread_mutex_unlock(&queue_lock);
            }
        }
    }
}

void* generate_Func(void* arg){
    bool request_E, request_L;
    bool result_E, result_L;
    bool proccessed_E, proccessed_L;

    runPythonScript(SCRIPT_PATH);

    if(pid != 0){
        sleep(8); //Timp necesar pentru initializare model.
        close(pipe_C_Python[0]); // Părintele nu citește din pipe-ul C_Python
        close(pipe_Python_C[1]); // Părintele nu scrie în pipe-ul Python_C

        char buffer_out_E[MAX_LINE_LENGTH], buffer_out_L[MAX_LINE_LENGTH]; // Buffer pentru scrierea către Python
        char buffer_in_E[MAX_LINE_LENGTH], buffer_in_L[MAX_LINE_LENGTH];  // Buffer pentru citirea de la Python
        ssize_t bytes_read;
        int exit_Flag = 0; //* Flag folosit pentru a astepta raspunsul de la python
        
        while(1){
            pthread_mutex_lock(&queue_lock);
            request_E = queue[0].request;
            request_L = queue[1].request;
            result_E = queue[0].result;
            result_L = queue[1].result;
            proccessed_E = queue[0].proccessed;
            proccessed_L = queue[1].proccessed;
            pthread_mutex_unlock(&queue_lock);
            
            if(request_E == true && proccessed_E == false){
                //* inseamna ca am request pentru intrare
                //* Oare am locuri in parcare?

                // acum campul request devine false, ca deja proecesez cererea
                //* Trimit comanda cu partea pe care vreau sa o procesez in stdout:
                strcpy(buffer_out_E, "left\n");
                printf("Părintele scrie către Python: %s", buffer_out_E);
                if (write(pipe_C_Python[1], buffer_out_E, strlen(buffer_out_E)) == -1) {
                    perror("Eroare la scriere in pipe_C_Python");
                    exit(EXIT_FAILURE);
                }
                
                //* Citesc si filtrez din pipe, rezultatul procesarii, ma uit doar dupa True sau False
                while(!exit_Flag){  
                    bytes_read = read(pipe_Python_C[0], buffer_in_E, sizeof(buffer_in_E) - 1);
                    if (bytes_read == -1) {
                        perror("Eroare la citirea din pipe_Python_C");
                        exit(EXIT_FAILURE);
                    }
                    buffer_in_E[bytes_read] = '\0';
                    if (strstr(buffer_in_E, "True") || strstr(buffer_in_E, "False")) {
                        //? Doar cand gasesc True sau False, e gata procesarea si pot sa ies din procesarea curenta
                        printf("Filtered C received: %s", buffer_in_E);
                        exit_Flag = 1;
                    }
                }
                exit_Flag = 0; //* Resetez flagul de citire din python

                if(strstr(buffer_in_E, "True")){
                    result_E = true;
                }
                else{
                    result_E =false;
                }

                proccessed_E = true;
            }

            if(request_L == true && proccessed_L == false){
                //* inseamna ca am request pentru iesire
                // acum campul de request devine false, ca deja procesez cererea
                //result_L = runPythonScript(SCRIPT_PATH);
                //* Trimit comanda partea pe care vreau sa o procesez in stdout:
                strcpy(buffer_out_L, "right\n");
                printf("Părintele scrie către Python: %s", buffer_out_L);
                if (write(pipe_C_Python[1], buffer_out_L, strlen(buffer_out_L)) == -1) {
                    perror("Eroare la scriere in pipe_C_Python");
                    exit(EXIT_FAILURE);
                }

                //* Citesc si filtrez din pipe, rezultatul procesarii
                while(!exit_Flag){  
                    bytes_read = read(pipe_Python_C[0], buffer_in_L, sizeof(buffer_in_L) - 1);
                    if (bytes_read == -1) {
                        perror("Eroare la citirea din pipe_Python_C");
                        exit(EXIT_FAILURE);
                    }
                    buffer_in_E[bytes_read] = '\0';
                    if (strstr(buffer_in_L, "True") || strstr(buffer_in_L, "False")) {
                        //? Doar cand gasesc True sau False, e gata procesarea si pot sa ies din procesarea curenta
                        printf("Filtered C received: %s", buffer_in_L);
                        exit_Flag = 1;
                    }
                }
                exit_Flag = 0; //* Resetez flagul de citire din python

                if(strstr(buffer_in_L, "True")){
                    result_L = true;
                }
                else{
                    result_L =false;
                }
                proccessed_L = true;
            }

            pthread_mutex_lock(&queue_lock);
            queue[1].proccessed = proccessed_L;
            queue[1].result = result_L;

            queue[0].proccessed = proccessed_E;
            queue[0].result = result_E;
            pthread_mutex_unlock(&queue_lock);
        }

        close(pipe_C_Python[1]);

        int status;
        if (waitpid(pid, &status, 0) == -1) {
            perror("Eroare la waitpid");
            exit(EXIT_FAILURE);
        }

        if (WIFEXITED(status)) {
            printf("Procesul copil (Python) a ieșit cu status: %d\n", WEXITSTATUS(status));
        } else if (WIFSIGNALED(status)) {
            printf("Procesul copil (Python) a fost terminat de semnalul: %d\n", WTERMSIG(status));
        } else {
            printf("Procesul copil (Python) a terminat anormal.\n");
        }

        //Închide și capătul de citire al pipe-ului Python -> C după ce s-a terminat comunicarea
        close(pipe_Python_C[0]);
    }
    return NULL;
}

void delay(int number_of_seconds)
{
	// Converting time into milli_seconds
	int milli_seconds = 1000 * number_of_seconds;

	// Storing start time
	clock_t start_time = clock();

	// looping till required time is not achieved
	while (clock() < start_time + milli_seconds);
}

void busy_delay_ms(long milliseconds) {
    long i;
    // This loop count is highly dependent on CPU speed.
    // Adjust as needed for your specific system.
    // Rough estimate: 1ms might be 1000-100000 iterations on a modern CPU.
    long loops_per_ms = 100000; // You'd need to calibrate this
    for (i = 0; i < milliseconds * loops_per_ms; i++) {
        // Do nothing
    }
}

/*
    Sa am un thread care imi citeste din seriala si imi adauga comenzile in coada
    Iar apoi, celalalt thread care pune mutex pe seriala cand vrea sa trimita comanda procesata
*/


/* Metoda cu timeout

    // Set up `select()` for timeout
        fd_set read_fds;
        FD_ZERO(&read_fds);
        FD_SET(pipe_Python_C[0], &read_fds);  // Monitor Python-to-C pipe for reading

        struct timeval timeout;
        timeout.tv_sec = 10;  // 5-second timeout
        timeout.tv_usec = 0;

        printf("Aștept răspuns de la Python (max 5 secunde)...\n");
        int ready = select(pipe_Python_C[0] + 1, &read_fds, NULL, NULL, &timeout);

        if (ready == -1) {
            perror("Eroare în select()");
            exit(EXIT_FAILURE);
        } else if (ready == 0) {
            printf("Timeout: Python nu a răspuns în 5 secunde.\n");
        } else {
            // Data is available to read
            bytes_read = read(pipe_Python_C[0], buffer_in_L, sizeof(buffer_in_L) - 1);
            if (bytes_read == -1) {
                perror("Eroare la citirea din pipe_Python_C");
                exit(EXIT_FAILURE);
            }
            if (bytes_read > 0) {
                buffer_in_L[bytes_read] = '\0';
                printf("Părintele a citit de la Python: %s", buffer_in_L);
            } else {
                printf("Python a închis pipe-ul (EOF).\n");
            }
        }
*/