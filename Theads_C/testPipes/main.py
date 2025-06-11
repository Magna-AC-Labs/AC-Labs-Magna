import sys
import os

try:
    while True:
        # Citim o linie
        line = sys.stdin.readline()
        
        if not line: #Verific daca am inchis pipe, adica nu am mai putut citi din el
            break # Ieșim din buclă

        line = line.rstrip('\n') # Elimină doar newline-ul de la sfârșit

        if line == "exit":
            break

        #Linie de test, sa vad daca comunica corect
        processed_line = line + "A\n"

        try:
            sys.stdout.write(processed_line)
            sys.stdout.flush()
        except BrokenPipeError:
            break # Ieșim din buclă, deoarece nu mai putem scrie

except KeyboardInterrupt:
    print("\nScript Python oprit de utilizator (Ctrl+C).")
except Exception as e:
    print(f"Python: O eroare neașteptată a apărut: {e}")

sys.exit(0) # Asigură o ieșire curată