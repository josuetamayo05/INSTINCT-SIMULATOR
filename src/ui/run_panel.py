import tkinter as tk

SPEEDS= {"Lenta": 500, "Normal":200, "Rápida": 50} # milisegundos

class RunPanel(tk.Frame):
    """Controles de la fase de ejecucion, como SetupPanel, solo avisa a la App"""
    def __init__(self, master, on_play_pause, on_step, on_reset, on_edit):
        super().__init__(master)

        tk.Label(self, text="Ejecución", font=("Helvetica", 13, "bold")).pack(anchor="w")
        self.play_button = tk.Button(self, text="▶ Play", command=on_play_pause)
        self.play_button.pack(fill="x", pady=(2, 2))
        self.step_button = tk.Button(self, text="Un tick", command=on_step)
        self.step_button.pack(fill="x", pady=2)

        tk.Label(self, text="Velocidad", font=("Helvetica", 13, "bold")).pack(anchor="w", pady=(10, 0))
        self.speed = tk.StringVar(value="Normal")
        for name in SPEEDS:
            tk.Radiobutton(self, text=name, value=name, variable=self.speed).pack(anchor="w")

        tk.Button(self, text="⟲ Reiniciar", command=on_reset).pack(fill="x", pady=(10, 2))
        tk.Button(self, text="✎ Volver a preparar", command=on_edit).pack(fill="x", pady=2)

    @property
    def delay_ms(self) -> int:
        return SPEEDS[self.speed.get()]

    def show_state(self, running: bool, finished: bool) -> None:
        """Ajusta los botones al estado de la simulacion"""
        self.play_button.config(text="⏸ Pausa" if running else "▶ Play",
                                state="disabled" if finished else "normal")
        self.step_button.config(state="disabled" if finished or running else "normal")