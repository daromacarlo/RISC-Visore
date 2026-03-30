import sys
import subprocess
import os
import tkinter as tk
from tkinter import filedialog, messagebox

def compile_asm_to_hex(asm_file_path, log_widget):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    rars_path = os.path.join(script_dir, 'rars.jar')
    output_file = asm_file_path.replace('.asm', '_compiled.txt')

    log_widget.insert(tk.END, f"--- Inizio Processo ---\n")
    log_widget.insert(tk.END, f"Cartella script: {script_dir}\n")
    
    if not os.path.exists(rars_path):
        log_widget.insert(tk.END, f"ERRORE: rars.jar NON TROVATO in {script_dir}\n", "error")
        return False
    command = ['java', '-jar', 'rars.jar', 'a', 'dump', '.text', 'HexText', output_file, asm_file_path]

    try:
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            cwd=script_dir,
            shell=True if os.name == 'nt' else False
        )
        if result.returncode != 0 or "Error" in result.stderr or "Error" in result.stdout:
            log_widget.insert(tk.END, "ERRORE DURANTE LA COMPILAZIONE:\n", "error")
            log_widget.insert(tk.END, result.stdout + result.stderr + "\n", "error")
            return False
        if os.path.exists(output_file):
            log_widget.insert(tk.END, f"SUCCESSO!\nFile creato: {os.path.basename(output_file)}\n", "success")
            with open(output_file, 'r') as f:
                preview = f.read(100) 
                log_widget.insert(tk.END, f"Anteprima dati:\n{preview}...\n")
            return True
        else:
            log_widget.insert(tk.END, "ERRORE: RARS non ha generato il file. Controlla la sintassi .asm\n", "error")
            return False

    except Exception as e:
        log_widget.insert(tk.END, f"ERRORE DI SISTEMA: {str(e)}\n", "error")
        return False

class RarsGui:
    def __init__(self, root):
        self.root = root
        self.root.title("RISC-V Compiler Debugger")
        self.root.geometry("650x500")

        tk.Label(root, text="RARS Compiler Interface", font=('Arial', 12, 'bold')).pack(pady=10)
        
        self.btn_select = tk.Button(root, text="CARICA .ASM E COMPILA", command=self.open_file, 
                                   bg="#0056b3", fg="white", font=('Arial', 10, 'bold'), padx=20, pady=10)
        self.btn_select.pack(pady=10)

        self.log_text = tk.Text(root, height=18, width=75, bg="#000", fg="#00ff00", font=('Consolas', 9))
        self.log_text.pack(pady=10, padx=10)
        
        self.log_text.tag_config("error", foreground="#ff4444")
        self.log_text.tag_config("success", foreground="#00ff00")

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Assembly files", "*.asm")])
        if file_path:
            self.log_text.delete(1.0, tk.END)
            compile_asm_to_hex(file_path, self.log_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = RarsGui(root)
    root.mainloop()