import tkinter as tk
from tkinter import ttk

class SetupPanel(tk.Frame):
    """Panel de la fase de preparacion, no toca el mundo: avisa a la App
    mediante callbacks (funciones que la App le pasa al crearlo)"""

    def __init__(self, master, catalog, on_map_selected, on_clear, on_start):
        super().__init__(master)

        # Mapa
        tk.Label(self, text="Mapa", font=("Helvetica", 13, "bold")).pack(anchor="w")
        self.map_choice = ttk.Combobox(self, state="readonly", values=sorted(catalog.maps))
        self.map_choice.pack(fill="x", pady=(2, 10))
        self.map_choice.bind("<<ComboboxSelected>>",
                             lambda e: on_map_selected(self.map_choice.get()))

        # Especie a colocar
        tk.Label(self, text="Especie", font=("Helvetica", 13, "bold")).pack(anchor="w")
        self.species = tk.StringVar()
        for name in sorted(catalog.species):
            tk.Radiobutton(self, text=name, value=name, variable=self.species).pack(anchor="w")
        if catalog.species:
            self.species.set(sorted(catalog.species)[0])

        tk.Label(self, text="Clic: colocar · Clic derecho: quitar",
                 fg="gray").pack(anchor="w", pady=(4, 10))

        tk.Button(self, text="Quitar todas", command=on_clear).pack(fill="x")
        self.start_button = tk.Button(self, text="Empezar ▶", command=on_start)
        self.start_button.pack(fill="x", pady=(4, 10))

        # Errores de carga
        tk.Label(self, text="Errores de carga", font=("Helvetica", 13, "bold")).pack(anchor="w")
        issues = tk.Text(self, width=34, height=10, wrap="word")
        issues.pack(fill="both", expand=True)
        if catalog.issues:
            for i in catalog.issues:
                issues.insert("end", f"{i.file}:{i.line}\n  {i.message}\n\n")
            issues.config(fg="#b91c1c")
        else:
            issues.insert("end", "Todo se cargó sin errores.")
        issues.config(state="disabled")   # solo lectura

        if not catalog.maps or not catalog.species:
            self.start_button.config(state="disabled")

    def select_map(self, name: str) -> None:
        self.map_choice.set(name)

    @property
    def selected_species(self) -> str:
        return self.species.get()