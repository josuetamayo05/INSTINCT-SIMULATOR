import copy
import tkinter as tk
from src.simulation.simulation import Simulation
from src.world.creature import Creature
from src.ui.map_view import MapView

class App(tk.Tk):
    def __init__(self, catalog):
        super().__init__()
        self.title("Instinct Simulator")
        self.catalog = catalog

        self.map_view = MapView(self, cell_size=32)
        self.map_view.pack(padx=10, pady=10)

        bar = tk.Frame(self)
        bar.pack(fill="x", padx=10, pady=(0, 10))
        tk.Button(bar, text="Un tick", command=self.on_tick).pack(side="left")
        self.status = tk.Label(bar, text="")
        self.status.pack(side="left", padx=10)

        self.sim = None
        self.refresh()

    def _demo_world(self):
        world = copy.deepcopy(next(iter(self.catalog.maps.values())))
        world.place_creature(Creature.from_program(self.catalog.species["Hobbit"]), 2, 2)
        world.place_creature(Creature.from_program(self.catalog.species["Uruk"]), 12, 4)
        return world

    def on_tick(self):
        self.sim.tick()
        self.refresh()

    def refresh(self):
        """Redibuja todo leyendo el estado de la simulacion"""
        self.map_view.draw(self.sim.world)
        alive = len(self.sim.world.alive_creatures())
        self.status.config(text=f"Tick {self.sim.tick_count} · {alive} vivas")