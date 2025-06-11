#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>     
#include <sys/wait.h> 

#define PYTHON_INTERPRETER "/usr/bin/python3"
#define SCRIPT_PATH "/Users/mariusfiat/Programming_Environment/Magna/Theads_C/testPipes/main.py"
#define MAX_LINE_LENGTH 256 

int main(void) {
    int pipe_C_Python[2]; // Pipe pentru C -> Python (C scrie, Python citește)
    int pipe_Python_C[2]; // Pipe pentru Python -> C (Python scrie, C citește)

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

    pid_t pid = fork(); // Creează procesul copil

    if (pid == -1) {
        perror("Eroare la fork");
        exit(EXIT_FAILURE);
    }

    if (pid == 0) { // Procesul copil (Python)
        // Închide capetele pipe-urilor pe care nu le folosește copilul
        close(pipe_C_Python[1]); // Copilul nu scrie în pipe-ul C_Python
        close(pipe_Python_C[0]); // Copilul nu citește din pipe-ul Python_C

        // Redirecționează stdin (0) al copilului către capătul de citire al pipe-ului C_Python
        if (dup2(pipe_C_Python[0], STDIN_FILENO) == -1) {
            perror("Eroare dup2 pipe_C_Python[0]");
            exit(EXIT_FAILURE);
        }
        // Redirecționează stdout (1) al copilului către capătul de scriere al pipe-ului Python_C
        if (dup2(pipe_Python_C[1], STDOUT_FILENO) == -1) {
            perror("Eroare dup2 pipe_Python_C[1]");
            exit(EXIT_FAILURE);
        }

        // Închide descriptorii originali după dup2
        close(pipe_C_Python[0]);
        close(pipe_Python_C[1]);

        // Execută scriptul Python
        execl(PYTHON_INTERPRETER, "python3", SCRIPT_PATH, NULL);

        // Dacă execl eșuează, se va ajunge aici
        perror("Eroare la execl (verifică calea interpreterului Python sau a scriptului)");
        exit(EXIT_FAILURE);
    } else { // Procesul părinte (C)
        // Închide capetele pipe-urilor pe care nu le folosește părintele
        close(pipe_C_Python[0]); // Părintele nu citește din pipe-ul C_Python
        close(pipe_Python_C[1]); // Părintele nu scrie în pipe-ul Python_C

        char buffer_out[MAX_LINE_LENGTH]; // Buffer pentru scrierea către Python
        char buffer_in[MAX_LINE_LENGTH];  // Buffer pentru citirea de la Python
        ssize_t bytes_read;

        // 1. Părintele scrie către Python
        strcpy(buffer_out, "aa\n");
        printf("Părintele scrie către Python: %s", buffer_out);
        if (write(pipe_C_Python[1], buffer_out, strlen(buffer_out)) == -1) {
            perror("Eroare la scriere in pipe_C_Python");
            exit(EXIT_FAILURE);
        }

        // 2. Părintele citește de la Python
        bytes_read = read(pipe_Python_C[0], buffer_in, sizeof(buffer_in) - 1);
        if (bytes_read == -1) {
            perror("Eroare la citirea din pipe_Python_C");
            exit(EXIT_FAILURE);
        }
        if (bytes_read > 0) {
            buffer_in[bytes_read] = '\0';
            printf("Părintele a citit de la Python: %s", buffer_in);
        } else {
            printf("Părintele nu a citit nimic de la Python (EOF sau pipe gol).\n");
        }
        
        //Inchid capatul de scriere dupa ce procesul parinte nu mai are de scris nimic.
        close(pipe_C_Python[1]);

        // Așteaptă terminarea procesului copil
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

        // Închide și capătul de citire al pipe-ului Python -> C după ce s-a terminat comunicarea
        close(pipe_Python_C[0]);
    }

    return 0;
}