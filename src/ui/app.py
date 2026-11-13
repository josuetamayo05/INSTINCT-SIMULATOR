import copy
import tkinter as tk
from src.simulation.simulation import Simulation
from src.world.creature import Creature
from src.ui.map_view import MapView
from src.ui.setup_panel import SetupPanel

class App(tk.Tk):
    def __init__(self, catalog):
        super().__init__()
        self.title("Instinct Simulator")
        self.catalog = catalog
        self.setup_world = None   # el mundo que se edita en la preparación
        self.sim = None           # None = fase de preparación

        self.setup_panel = SetupPanel(self, catalog,
                                      on_map_selected=self.select_map,
                                      on_clear=self.clear_creatures,
                                      on_start=self.start)
        self.setup_panel.pack(side="left", fill="y", padx=10, pady=10)

        right = tk.Frame(self)
        right.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)
        self.map_view = MapView(right, cell_size=32)
        self.map_view.pack()
        self.map_view.bind("<Button-1>", self.on_left_click)
        for button in ("<Button-2>", "<Button-3>", "<Control-Button-1>"):
            self.map_view.bind(button, self.on_right_click)   # clic derecho 

        bar = tk.Frame(right)
        bar.pack(fill="x", pady=(10, 0))
        self.tick_button = tk.Button(bar, text="Un tick", command=self.on_tick, state="disabled")
        self.tick_button.pack(side="left")
        self.status = tk.Label(bar, text="", anchor="w")
        self.status.pack(side="left", padx=10)

        if catalog.maps:
            first = sorted(catalog.maps)[0]
            self.setup_panel.select_map(first)
            self.select_map(first)
        else:
            self.show_message("No se cargó ningún mapa. Revisa los errores.")


    # Fase de preparación

    def select_map(self, name: str) -> None:
        # Copia: así el mapa del catálogo queda limpio para volver a elegirlo
        self.setup_world = copy.deepcopy(self.catalog.maps[name])
        self.refresh()

    def on_left_click(self, event) -> None:
        if self.sim is not None or self.setup_world is None:
            return
        x, y = self.map_view.cell_at(event.x, event.y)
        species = self.setup_panel.selected_species
        creature = Creature.from_program(self.catalog.species[species])
        if self.setup_world.place_creature(creature, x, y):
            self.refresh()
        else:
            self.show_message(f"No se puede colocar en ({x}, {y}): está ocupada.")

    def on_right_click(self, event) -> None:
        if self.sim is not None or self.setup_world is None:
            return
        x, y = self.map_view.cell_at(event.x, event.y)
        cell = self.setup_world.get_cell(x, y)
        if cell and cell.creature:
            self.setup_world.remove_creature(cell.creature)
            self.refresh()

    def clear_creatures(self) -> None:
        if self.sim is not None or self.setup_world is None:
            return
        for c in list(self.setup_world.creatures):
            self.setup_world.remove_creature(c)
        self.refresh()

    def start(self) -> None:
        if not self.setup_world or not self.setup_world.creatures:
            self.show_message("Coloca al menos una criatura antes de empezar.")
            return
        self.sim = Simulation(self.setup_world, seed=1)
        self.tick_button.config(state="normal")
        self.refresh()

    # Fase de ejecución 

    def on_tick(self) -> None:
        self.sim.tick()
        self.refresh()

    # Dibujo

    def refresh(self) -> None:
        """Redibuja leyendo el mundo de la fase actual."""
        world = self.sim.world if self.sim else self.setup_world
        if world is None:
            return
        self.map_view.draw(world)
        alive = len(world.alive_creatures())
        if self.sim:
            self.show_message(f"Tick {self.sim.tick_count} · {alive} vivas")
        else:
            self.show_message(f"Preparación · {alive} criaturas colocadas")

    def show_message(self, text: str) -> None:
        self.status.config(text=text)