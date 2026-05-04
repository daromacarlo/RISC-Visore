import serial
import time
import os
import shutil
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import re

# --- CONFIGURAZIONE ---
PORTA = 'COM3' 
BAUD = 115200
# FQBN aggiornato per abilitare l'USB CDC (fondamentale per ESP32-C3 SuperMini)
FQBN = 'esp32:esp32:esp32c3:CDCOnBoot=cdc' 

def apri_in_editor(file_path):
    """Apre il file con l'editor di testo predefinito (Blocco Note su Windows)."""
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(['code', file_path])
        else:  # macOS / Linux
            subprocess.run(['xdg-open', file_path])
    except Exception as e:
        print(f"Errore nell'apertura dell'editor: {e}")

# --- LOGICA DI COMPILAZIONE E UPLOAD ---
def compile_logic(asm_file_path, log_widget):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    rars_path = os.path.join(script_dir, 'rars.jar')
    
    # Il file di lavoro sarà sempre riscv1.S nella cartella dello script
    s_file_path = os.path.join(script_dir, 'riscv1.S')
    
    try:
        # 1. Legge il contenuto del file .asm selezionato
        with open(asm_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 2. TRADUZIONE: Sostituisce 'main' con 'riscvprg'
        new_content = content.replace('main', 'riscvprg')
        
        # 3. Salva il risultato nel file fisso riscv1.S
        with open(s_file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        log_widget.insert(tk.END, f"Copia creata: riscv1.S (Label 'main' sostituita con 'riscvprg')\n")
    except Exception as e:
        log_widget.insert(tk.END, f"ERRORE nella preparazione del file .S: {e}\n", "error")
        return None
    
    # --- COMPILAZIONE E FLASH ARDUINO (ESP32-C3) ---
    validator_path = os.path.join(script_dir, 'validator.ino')
    if not os.path.exists(validator_path):
        log_widget.insert(tk.END, "ERRORE: validator.ino non trovato nella cartella dello script!\n", "error")
        return None

    log_widget.insert(tk.END, "\n--- Avvio Compilazione e Flash su ESP32-C3 ---\n")
    log_widget.insert(tk.END, "Compilazione validator.ino (attendi qualche istante)...\n")
    log_widget.see(tk.END)
    
    use_shell = True if os.name == 'nt' else False

    try:
        # Step 1: Compilazione Sketch Arduino
        res_comp = subprocess.run(
            ["arduino-cli", "compile", "--fqbn", FQBN, validator_path], 
            capture_output=True, text=True, cwd=script_dir, shell=use_shell
        )
        if res_comp.returncode != 0:
            log_widget.insert(tk.END, "ERRORE COMPILAZIONE ARDUINO:\n" + res_comp.stderr + "\n", "error")
            return None
        
        log_widget.insert(tk.END, "Compilazione Arduino completata. Avvio caricamento...\n")
        log_widget.see(tk.END)

        # Step 2: Caricamento sulla scheda (Upload)
        res_up = subprocess.run(
            ["arduino-cli", "upload", "-p", PORTA, "--fqbn", FQBN, validator_path], 
            capture_output=True, text=True, cwd=script_dir, shell=use_shell
        )
        if res_up.returncode != 0:
            log_widget.insert(tk.END, "ERRORE CARICAMENTO ARDUINO:\n" + res_up.stderr + "\n", "error")
            return None

        log_widget.insert(tk.END, "Caricamento su ESP32-C3 completato con successo!\n")
        
    except FileNotFoundError:
        log_widget.insert(tk.END, "ERRORE CRITICO: comando 'arduino-cli' non trovato.\nAssicurati che Arduino CLI sia installato e nel PATH.\n", "error")
        return None
    except Exception as e:
        log_widget.insert(tk.END, f"ERRORE DI SISTEMA ARDUINO: {e}\n", "error")
        return None
    # -----------------------------------------------

    # Il file compilato (HexText) da RARS avrà un nome fisso basato su riscv1
    output_file = os.path.join(script_dir, 'riscv1_compiled.txt')

    log_widget.insert(tk.END, f"\n--- Avvio Compilazione RARS ---\n")
    if not os.path.exists(rars_path):
        log_widget.insert(tk.END, f"ERRORE: rars.jar non trovato in {script_dir}\n", "error")
        return None

    # Esegue RARS sul file generato riscv1.S
    command = ['java', '-jar', 'rars.jar', 'a', 'dump', '.text', 'HexText', output_file, s_file_path]
    try:
        result = subprocess.run(command, capture_output=True, text=True, cwd=script_dir, shell=use_shell)
        if result.returncode != 0:
            log_widget.insert(tk.END, "ERRORE DI COMPILAZIONE RARS:\n", "error")
            log_widget.insert(tk.END, result.stderr + "\n", "error")
            return None
        return output_file
    except Exception as e:
        log_widget.insert(tk.END, f"ERRORE DI SISTEMA JAVA: {str(e)}\n", "error")
    return None

# --- LOGICA DI COMPILAZIONE E UPLOAD MULTIPLE ---
def compile_logic_multiple(asm_file_path, log_widget, data):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    rars_path = os.path.join(script_dir, 'rars.jar')
    
    # Il file di lavoro sarà sempre riscv1.S nella cartella dello script
    s_file_path = os.path.join(script_dir, 'riscv1.S')
    
    try:
        # 1. Legge il contenuto del file .asm selezionato
        with open(asm_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 2. TRADUZIONE: Sostituisce 'main' con 'riscvprg'
        new_content = content.replace('main', 'riscvprg')
        
# 3. INSERIMENTO DATI NELLA SEZIONE .data
        if data:
            # Cerca la direttiva .data all'inizio di una riga, ignorando quelle nei commenti (#)
            match = re.search(r'^\s*\.data\b', new_content, re.MULTILINE)
            
            if match:
                # Trova la fine della parola .data vera e propria e inserisce la stringa subito dopo
                insert_pos = match.end()
                new_content = new_content[:insert_pos] + "\n    " + data + "\n" + new_content[insert_pos:]
                log_widget.insert(tk.END, "Dati iniettati con successo nella sezione .data esistente\n")
            else:
                # Se non esiste una sezione .data, la creiamo in fondo in automatico
                new_content += "\n\n.data\n    " + data + "\n"
                log_widget.insert(tk.END, "Sezione .data non trovata: creata in automatico e dati iniettati.\n")
        # 4. Salva il risultato nel file fisso riscv1.S
        with open(s_file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        log_widget.insert(tk.END, f"Copia creata: riscv1.S (Label 'main' sostituita con 'riscvprg')\n")
    except Exception as e:
        log_widget.insert(tk.END, f"ERRORE nella preparazione del file .S: {e}\n", "error")
        return None
    
    # --- COMPILAZIONE E FLASH ARDUINO (ESP32-C3) ---
    validator_path = os.path.join(script_dir, 'validator.ino')
    if not os.path.exists(validator_path):
        log_widget.insert(tk.END, "ERRORE: validator.ino non trovato nella cartella dello script!\n", "error")
        return None

    log_widget.insert(tk.END, "\n--- Avvio Compilazione e Flash su ESP32-C3 ---\n")
    log_widget.insert(tk.END, "Compilazione validator.ino (attendi qualche istante)...\n")
    log_widget.see(tk.END)
    
    use_shell = True if os.name == 'nt' else False

    try:
        # Step 1: Compilazione Sketch Arduino
        res_comp = subprocess.run(
            ["arduino-cli", "compile", "--fqbn", FQBN, validator_path], 
            capture_output=True, text=True, cwd=script_dir, shell=use_shell
        )
        if res_comp.returncode != 0:
            log_widget.insert(tk.END, "ERRORE COMPILAZIONE ARDUINO:\n" + res_comp.stderr + "\n", "error")
            return None
        
        log_widget.insert(tk.END, "Compilazione Arduino completata. Avvio caricamento...\n")
        log_widget.see(tk.END)

        # Step 2: Caricamento sulla scheda (Upload)
        res_up = subprocess.run(
            ["arduino-cli", "upload", "-p", PORTA, "--fqbn", FQBN, validator_path], 
            capture_output=True, text=True, cwd=script_dir, shell=use_shell
        )
        if res_up.returncode != 0:
            log_widget.insert(tk.END, "ERRORE CARICAMENTO ARDUINO:\n" + res_up.stderr + "\n", "error")
            return None

        log_widget.insert(tk.END, "Caricamento su ESP32-C3 completato con successo!\n")
        
    except FileNotFoundError:
        log_widget.insert(tk.END, "ERRORE CRITICO: comando 'arduino-cli' non trovato.\nAssicurati che Arduino CLI sia installato e nel PATH.\n", "error")
        return None
    except Exception as e:
        log_widget.insert(tk.END, f"ERRORE DI SISTEMA ARDUINO: {e}\n", "error")
        return None
    # -----------------------------------------------

    # Il file compilato (HexText) da RARS avrà un nome fisso basato su riscv1
    output_file = os.path.join(script_dir, 'riscv1_compiled.txt')

    log_widget.insert(tk.END, f"\n--- Avvio Compilazione RARS ---\n")
    if not os.path.exists(rars_path):
        log_widget.insert(tk.END, f"ERRORE: rars.jar non trovato in {script_dir}\n", "error")
        return None

    # Esegue RARS sul file generato riscv1.S
    command = ['java', '-jar', 'rars.jar', 'a', 'dump', '.text', 'HexText', output_file, s_file_path]
    try:
        result = subprocess.run(command, capture_output=True, text=True, cwd=script_dir, shell=use_shell)
        if result.returncode != 0:
            log_widget.insert(tk.END, "ERRORE DI COMPILAZIONE RARS:\n", "error")
            log_widget.insert(tk.END, result.stderr + "\n", "error")
            return None
        return output_file
    except Exception as e:
        log_widget.insert(tk.END, f"ERRORE DI SISTEMA JAVA: {str(e)}\n", "error")
    return None

# --- APPLICAZIONE PRINCIPALE ---
class RiscVMultiTool:
    def __init__(self, root):
        self.root = root
        self.root.title("RISC-Visore")
        self.root.geometry("650x650")
        
        self.container = tk.Frame(self.root)
        self.container.pack(fill="both", expand=True)
        
        self.show_launcher()

    def clear_frame(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_launcher(self):
        self.clear_frame()
        tk.Label(self.container, text="RISC-Visore", font=('Arial', 16, 'bold')).pack(pady=40)
        
        btn_style = {"width": 30, "font": ('Arial', 10), "pady": 10}

        tk.Button(self.container, text="MODALITÀ NO CONTROLLI (.asm)\n Compila + Invia (NO controlli) ", 
                  bg="#E64F8E", fg="white", command=self.show_asm_nocontrol_page, **btn_style).pack(pady=10)

        tk.Button(self.container, text="MODALITÀ ASSEMBLY (.asm)\nCompila + Invia", 
                  bg="#cc9d04", fg="white", command=self.show_asm_page, **btn_style).pack(pady=10)
        
        tk.Button(self.container, text="MODALITÀ MULTIPLA (.asm)\nSet test + Compila + Invia ", 
                  bg="#008d2a", fg="white", command=self.show_asm_multiple_page, **btn_style).pack(pady=10)

        tk.Button(self.container, text="MODALITÀ DIRETTA (.hex)\nInvia hex (NO compilazione)", 
                  bg="#023058", fg="white", command=self.show_hex_page, **btn_style).pack(pady=10)

        tk.Button(self.container, text="MODALITÀ TEST\nTest led ", 
                  bg="#4B5551", fg="white", command=self.show_test_page, **btn_style).pack(pady=10)


    def show_asm_nocontrol_page(self):
        self.clear_frame()
        self.asm_path = None
        
        tk.Button(self.container, text="⬅ Torna al Menu", command=self.show_launcher).pack(anchor="w", padx=10, pady=5)
        tk.Label(self.container, text="Caricamento codice Assembly per esecuzione senza controlli", font=('Arial', 12, 'bold')).pack()

        self.btn_select = tk.Button(self.container, text="1. SELEZIONA FILE .ASM", command=self.seleziona_asm)
        self.btn_select.pack(pady=5)
        
        self.label_file = tk.Label(self.container, text="Nessun file", fg="gray")
        self.label_file.pack()

        self.btn_run = tk.Button(self.container, text="2. COMPILA, FLASH E INVIA", state=tk.DISABLED, 
                                bg="#28a745", fg="white", command=self.process_asm_nocontrol)
        self.btn_run.pack(pady=10)

        self.log_area = scrolledtext.ScrolledText(self.container, height=15, bg="black", fg="#00ff00")
        self.log_area.pack(padx=10, pady=10, fill="both", expand=True)
        self.log_area.tag_config("error", foreground="red")

    def show_asm_multiple_page(self):
        self.clear_frame()
        self.asm_path = None
        
        tk.Button(self.container, text="⬅ Torna al Menu", command=self.show_launcher).pack(anchor="w", padx=10, pady=5)
        tk.Label(self.container, text="Caricamento codice Assembly per esecuzione multipla", font=('Arial', 12, 'bold')).pack()

        self.btn_select = tk.Button(self.container, text="1. SELEZIONA FILE .ASM", command=self.seleziona_asm)
        self.btn_select.pack(pady=5)

        tk.Label(self.container, text="2. INSERISCI .DATA DI TEST (separati da ';')", font=('Arial', 10, 'bold')).pack(pady=(10, 0))
        
        # Area di testo per i set di dati
        self.data_input_area = scrolledtext.ScrolledText(self.container, height=5, bg="white", fg="black")
        self.data_input_area.pack(padx=20, pady=5, fill="x")
        self.data_input_area.insert(tk.END, "Esempio: vettore:    .word 15, 20, 42, 90, 88, 10, 40... (elimina per inserire i dati)") # Testo di esempio opzionale
        
        self.label_file = tk.Label(self.container, text="Nessun file", fg="gray")
        self.label_file.pack()

        self.btn_run = tk.Button(self.container, text="2. COMPILA, FLASH E INVIA", state=tk.DISABLED, 
                                bg="#28a745", fg="white", command=self.process_asm_multiple)
        self.btn_run.pack(pady=10)

        self.log_area = scrolledtext.ScrolledText(self.container, height=15, bg="black", fg="#00ff00")
        self.log_area.pack(padx=10, pady=10, fill="both", expand=True)
        self.log_area.tag_config("error", foreground="red")

    def show_asm_page(self):
        self.clear_frame()
        self.asm_path = None
        
        tk.Button(self.container, text="⬅ Torna al Menu", command=self.show_launcher).pack(anchor="w", padx=10, pady=5)
        tk.Label(self.container, text="Caricamento codice Assembly", font=('Arial', 12, 'bold')).pack()

        self.btn_select = tk.Button(self.container, text="1. SELEZIONA FILE .ASM", command=self.seleziona_asm)
        self.btn_select.pack(pady=5)
        
        self.label_file = tk.Label(self.container, text="Nessun file", fg="gray")
        self.label_file.pack()

        self.btn_run = tk.Button(self.container, text="2. COMPILA, FLASH E INVIA", state=tk.DISABLED, 
                                bg="#28a745", fg="white", command=self.process_asm)
        self.btn_run.pack(pady=10)

        self.log_area = scrolledtext.ScrolledText(self.container, height=15, bg="black", fg="#00ff00")
        self.log_area.pack(padx=10, pady=10, fill="both", expand=True)
        self.log_area.tag_config("error", foreground="red")

    def show_test_page(self):
        self.clear_frame()
        
        # Pulsante per tornare al menu
        tk.Button(self.container, text="⬅ Torna al Menu", command=self.show_launcher).pack(anchor="w", padx=10, pady=5)
        
        tk.Label(self.container, text="Diagnostica Hardware ESP32", font=('Arial', 14, 'bold')).pack(pady=20)

        # UNICO GRANDE TASTO
        self.btn_run = tk.Button(
            self.container, 
            text="AVVIA SEQUENZA TEST LED", 
            bg="#007bff", 
            fg="white", 
            font=('Arial', 16, 'bold'),
            width=30,
            height=6,
            command=self.process_test  # Chiama process_test che avvia il thread
        )
        self.btn_run.pack(pady=30)

        # Area di log per vedere la risposta "Test completato" dell'Arduino
        self.log_area = scrolledtext.ScrolledText(self.container, height=12, bg="black", fg="#00ff00", font=('Consolas', 10))
        self.log_area.pack(padx=10, pady=10, fill="both", expand=True)
            
    def seleziona_asm(self):
        path = filedialog.askopenfilename(filetypes=[("Assembly", "*.asm")])
        if path:
            self.asm_path = path
            self.label_file.config(text=os.path.basename(path), fg="black")
            self.btn_run.config(state=tk.NORMAL)

    def process_asm(self):
        if messagebox.askyesno("Modifica", "Vuoi modificare il file prima di compilarlo?"):
            apri_in_editor(self.asm_path)
            messagebox.showinfo("Pronto", "Clicca OK dopo aver salvato e chiuso il file per continuare.")
        
        self.btn_run.config(state=tk.DISABLED) # Disabilita per prevenire doppi click
        threading.Thread(target=self._worker_asm, daemon=True).start()

    def process_asm_nocontrol(self):
        if messagebox.askyesno("Modifica", "Vuoi modificare il file prima di compilarlo?"):
            apri_in_editor(self.asm_path)
            messagebox.showinfo("Pronto", "Clicca OK dopo aver salvato e chiuso il file per continuare.")
        
        self.btn_run.config(state=tk.DISABLED) # Disabilita per prevenire doppi click
        threading.Thread(target=self._worker_asm_nocontrol, daemon=True).start()

    def process_asm_multiple(self):
        if messagebox.askyesno("Modifica", "Vuoi modificare il file prima di compilarlo?"):
            apri_in_editor(self.asm_path)
            messagebox.showinfo("Pronto", "Clicca OK dopo aver salvato e chiuso il file per continuare.")
        
        # LEGGIAMO I DATI NEL THREAD PRINCIPALE
        raw_data = self.data_input_area.get("1.0", tk.END).strip()
        
        # Ignoriamo il placeholder di esempio se l'utente non l'ha sovrascritto
        if raw_data.startswith("Esempio:"):
            raw_data = ""
            
        self.btn_run.config(state=tk.DISABLED) # Disabilita per prevenire doppi click
        # Passiamo i dati estratti al thread secondario come argomento
        threading.Thread(target=self._worker_asm_multiple, args=(raw_data,), daemon=True).start()

    def process_test(self):
        self.btn_run.config(state=tk.DISABLED) # Disabilita per prevenire doppi click
        threading.Thread(target=self._worker_test, daemon=True).start()

    def _worker_asm(self):
        hex_file = compile_logic(self.asm_path, self.log_area)
        if hex_file:
            self._send_to_serial(hex_file, mode= "ASM")
        self.btn_run.config(state=tk.NORMAL) # Riabilita a fine esecuzione

    def _worker_asm_nocontrol(self):
        hex_file = compile_logic(self.asm_path, self.log_area)
        if hex_file:
            self._send_to_serial(hex_file, mode= "ANC")
        self.btn_run.config(state=tk.NORMAL) # Riabilita a fine esecuzione

    def _worker_asm_multiple(self, data_to_inject):
        # Dividiamo i dati usando il punto e virgola come separatore
        # Questo preserva la sintassi standard degli array Assembly separati da virgole
        datasets = [d.strip() for d in data_to_inject.split(';') if d.strip()]
        
        if not datasets:
            self.log_area.insert(tk.END, "Nessun dato multiplo inserito. Verrà eseguita una compilazione standard.\n")
            datasets = [""] # Se non c'è nulla, eseguiamo almeno il codice base

        # Ciclo su tutti i set di test forniti
        for i, data in enumerate(datasets):
            self.log_area.insert(tk.END, f"\n{'='*50}\n")
            self.log_area.insert(tk.END, f" ESECUZIONE SET DI TEST {i+1} DI {len(datasets)}\n")
            if data:
                self.log_area.insert(tk.END, f" Payload: {data}\n")
            self.log_area.insert(tk.END, f"{'='*50}\n")
            self.log_area.see(tk.END)
            
            # 1. Chiama la logica che modifica il file e compila (per questo specifico set)
            hex_file = compile_logic_multiple(self.asm_path, self.log_area, data)
            
            # 2. Se la compilazione ha avuto successo, invia alla seriale
            if hex_file:
                self._send_to_serial(hex_file, mode="AMU")
            else:
                self.log_area.insert(tk.END, f"ERRORE nel set di test {i+1}. Salto al prossimo.\n", "error")
            
            # Breve pausa per permettere alla scheda ESP32 di stabilizzarsi prima del prossimo reset/upload
            if i < len(datasets) - 1:
                time.sleep(2)

        self.log_area.insert(tk.END, f"\n{'='*50}\n")
        self.log_area.insert(tk.END, " TUTTI I SET DI TEST SONO STATI COMPLETATI\n")
        self.log_area.insert(tk.END, f"{'='*50}\n")
        self.btn_run.config(state=tk.NORMAL) # Riabilita il pulsante alla fine del batch

    def _worker_test(self):
        """Invia solo il comando di test senza compilare nulla."""
        try:
            self.log_area.insert(tk.END, f"Apertura porta {PORTA} per test rapido...\n")
            ser = serial.Serial(PORTA, BAUD, timeout=0.1)
            comando_test = "TST:START\n" 
            
            ser.write(comando_test.encode('utf-8'))
            self.log_area.see(tk.END)

            start_time = time.time()
            while time.time() - start_time < 10:
                if ser.in_waiting > 0:
                    line = ser.readline().decode(errors='ignore').strip()
                    if line:
                        self.log_area.insert(tk.END, f"ESP32 > {line}\n")
                        self.log_area.see(tk.END)
                        if "Test completato" in line:
                            break
            
            ser.close()
            self.log_area.insert(tk.END, "--- Test Terminato ---\n")
        except Exception as e:
            self.log_area.insert(tk.END, f"ERRORE SERIALE: {e}\n", "error")
        

        self.btn_run.config(state=tk.NORMAL)
    def show_hex_page(self):
        self.clear_frame()
        self.hex_path = None
        
        tk.Button(self.container, text="⬅ Torna al Menu", command=self.show_launcher).pack(anchor="w", padx=10, pady=5)
        tk.Label(self.container, text="Caricamento Esadecimale", font=('Arial', 12, 'bold')).pack()
        tk.Button(self.container, text="SELEZIONA FILE .HEX / .BIN", command=self.seleziona_hex).pack(pady=5)
        
        self.label_hex = tk.Label(self.container, text="Nessun file", fg="gray")
        self.label_hex.pack()


        self.btn_send_hex = tk.Button(self.container, text="INVIA A SCHEDA", state=tk.DISABLED, 
                                     bg="#28a745", fg="white", command=self.process_hex)
        self.btn_send_hex.pack(pady=10)

        self.log_area_hex = scrolledtext.ScrolledText(self.container, height=15, bg="black", fg="#00ff00")
        self.log_area_hex.pack(padx=10, pady=10, fill="both", expand=True)

    def seleziona_hex(self):
        path = filedialog.askopenfilename()
        if path:
            self.hex_path = path
            self.label_hex.config(text=os.path.basename(path))
            self.btn_send_hex.config(state=tk.NORMAL)

    def process_hex(self):
        if messagebox.askyesno("Modifica", "Vuoi visualizzare/modificare il file hex prima di inviarlo?"):
            apri_in_editor(self.hex_path)
        
        self.btn_send_hex.config(state=tk.DISABLED)
        threading.Thread(target=self._worker_hex, daemon=True).start()

    def _worker_hex(self):
        self._send_to_serial(self.hex_path, False)
        self.btn_send_hex.config(state=tk.NORMAL)

    def _send_to_serial(self, file_path, mode):
        # Sceglie il log in base alla modalità
        log_widget = self.log_area if mode in ["ASM", "ANC", "AMU"] else self.log_area_hex
        
        try:
            log_widget.insert(tk.END, f"\nConnessione su {PORTA}...\n")
            ser = serial.Serial(PORTA, BAUD, timeout=0.1)

            # Lettura e processamento file
            if mode in ["ASM", "ANC", "AMU"]: # Modalità ASM/NoControl/Multiple
                with open(file_path, 'r', encoding='utf-8') as f:
                    righe = f.readlines()
                    # Inversione byte per RISC-V (Little Endian)
                    data = "".join([r.strip()[6:8]+r.strip()[4:6]+r.strip()[2:4]+r.strip()[0:2] 
                                   for r in righe if len(r.strip())==8])
                    prefix = "ANC:" if mode == "ANC" else "ASM:" if mode == "ASM" else "AMU:"
                    final_payload = prefix + data
            else: # Modalità HEX diretta
                with open(file_path, 'rb') as f:
                    data = f.read().hex()
                    final_payload = "HEX:" + data

            ser.write(final_payload.encode('utf-8') + b'\n')
            log_widget.insert(tk.END, "Dati inviati. In attesa di risposta dall'ESP32...\n")
            
            start = time.time()
            while time.time() - start < 15:
                if ser.in_waiting > 0:
                    line = ser.readline().decode(errors='ignore').strip()
                    if line: 
                        log_widget.insert(tk.END, f"ESP32 > {line}\n")
                        log_widget.see(tk.END)
                        if "completata" in line.lower() or "42" in line: 
                            break
            ser.close()
            log_widget.insert(tk.END, "--- Sessione conclusa ---\n")
            log_widget.see(tk.END)
        except Exception as e:
            log_widget.insert(tk.END, f"ERRORE SERIALE: {e}\n", "error")

if __name__ == "__main__":
    root = tk.Tk()
    app = RiscVMultiTool(root)
    root.mainloop()