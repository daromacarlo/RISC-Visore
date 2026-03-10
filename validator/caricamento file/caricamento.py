import serial
import time
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading

PORTA = 'COM3' 
BAUD = 115200

class SerialApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RISC-Visore Monitor")
        self.root.geometry("500x400")

        self.file_path = None
        self.ser = None

        self.btn_select = tk.Button(root, text="Seleziona File .bin/.hex", command=self.seleziona_file)
        self.btn_select.pack(pady=5)

        self.label_file = tk.Label(root, text="Nessun file selezionato")
        self.label_file.pack()

        self.btn_send = tk.Button(root, text="Invia e Monitora", command=self.invia_file)
        self.btn_send.pack(pady=5)

        self.log_area = scrolledtext.ScrolledText(root, height=15)
        self.log_area.pack(fill="both", expand=True, padx=10, pady=10)

    def log(self, messaggio):
        self.log_area.insert(tk.END, messaggio + "\n")
        self.log_area.see(tk.END)

    def seleziona_file(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            self.label_file.config(text=self.file_path)

    def invia_file(self):
        if not self.file_path:
            messagebox.showerror("Errore", "Seleziona un file!")
            return
        threading.Thread(target=self._invia_thread, daemon=True).start()

    def _invia_thread(self):
        try:
            self.log("Tentativo di connessione...")
            self.ser = serial.Serial(PORTA, BAUD, timeout=0.1)
            time.sleep(2)
            
            with open(self.file_path, 'rb') as f:
                contenuto_hex = f.read().hex() + '\n'

            self.log(f"Invio di {len(contenuto_hex)} caratteri...")
            self.ser.write(contenuto_hex.encode('utf-8'))

            # Lettura continua dei log dalla scheda
            while self.ser.is_open:
                if self.ser.in_waiting > 0:
                    riga = self.ser.readline().decode(errors='ignore').strip()
                    if riga:
                        self.log(f"ESP32 > {riga}")
                        if "Sequenza completata" in riga:
                            break
                time.sleep(0.01)

            self.ser.close()
            self.log("Connessione chiusa correttamente.")

        except Exception as e:
            self.log(f"ERRORE: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialApp(root)
    root.mainloop()