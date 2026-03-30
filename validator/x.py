import subprocess
import os

# --- CONFIGURAZIONE ---
SKETCH_NAME = "validator.ino"
BOARD_TAG = "esp32:esp32:esp32c3" # Il "FQBN" per l'ESP32-C3
PORT = "COM3"                    # La porta dello screenshot

def run_command(command):
    """Esegue un comando e stampa l'output in tempo reale."""
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True)
        for line in process.stdout:
            print(line, end="")
        process.wait()
        return process.returncode == 0
    except Exception as e:
        print(f"Errore durante l'esecuzione: {e}")
        return False

def main():
    # 1. Verifica che il file esista
    if not os.path.exists(SKETCH_NAME):
        print(f"Errore: {SKETCH_NAME} non trovato nella cartella corrente!")
        return

    # 2. COMPILAZIONE
    print(f"\n--- [1/2] Compilazione in corso per {BOARD_TAG} ---")
    compile_cmd = f"arduino-cli compile --fqbn {BOARD_TAG} {SKETCH_NAME}"
    
    if run_command(compile_cmd):
        print("\n--- [OK] Compilazione riuscita! ---")
        
        # 3. CARICAMENTO
        print(f"\n--- [2/2] Caricamento su {PORT} ---")
        upload_cmd = f"arduino-cli upload -p {PORT} --fqbn {BOARD_TAG} {SKETCH_NAME}"
        
        if run_command(upload_cmd):
            print("\n--- [FINITO] Programma caricato con successo! ---")
        else:
            print("\n--- [ERRORE] Caricamento fallito. ---")
    else:
        print("\n--- [ERRORE] Compilazione fallita. Controlla gli errori nel codice. ---")

if __name__ == "__main__":
    main()