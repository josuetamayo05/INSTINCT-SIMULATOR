import tkinter as tk

class LogPanel(tk.Frame):
    """Texto de solo lectura con barra de desplazamiento"""

    def __init__(self, master, height:int = 8):
        super().__init__(master)
        tk.Label(self, text="Registro", font=("Helvetica", 13, "bold")).pack(anchor="w")
        body = tk.Frame(self)
        body.pack(fill="both", expand=True)
        scroll = tk.Scrollbar(body)
        scroll.pack(side="right", fill="y")
        self.text = tk.Text(body, height=height, wrap="word", state="disabled", yscrollcommand=scroll.set)
        self.text.pack(side="left", fill="both", expand=True)
        scroll.config(command=self.text.yview)

    def append(self,lines)-> None:
        if not lines: 
            return
        self.text.config(state="normal")
        for line in lines:
            self.text.insert("end", line + "\n")
        self.text.config(state="disabled")
        self.text.see("end") # hasta el ultimo 

    def clear(self) -> None:
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.config(state="disabled")