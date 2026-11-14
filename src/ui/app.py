import copy
import tkinter as tk
from src.simulation.simulation import Simulation
from src.world.creature import Creature
from src.ui.map_view import MapView
from src.ui.setup_panel import SetupPanel
from src.ui.run_panel import RunPanel
from src.ui.log_panel import LogPanel
class App(tk.Tk):
    def __init__(self, catalog):
        super().__init__()
        self.title("Instinct Simulator")
        self.geometry("1100x720")
        self.minsize(800, 520)
        self.catalog = catalog
        self.setup_world = None   # el mundo que se edita en la preparación
        self.sim = None           # None = fase de preparación
        self.running= False       # Esta en play?  
        self._after_id = None     # temporizador pendiente de tkinter
        self._events_shown = 0    # cuantos eventos ya estan en el registro

        # Columna izquierda: se muestra un panel u otro segun la fase
        self.side = tk.Frame(self)
        self.side.pack(side="left", fill="y", padx=10, pady=10)
        self.setup_panel = SetupPanel(self.side, catalog,
                                      on_map_selected=self.select_map,
                                      on_clear=self.clear_creatures,
                                      on_start=self.start)
        self.run_panel = RunPanel(self.side,
                                  on_play_pause=self.toggle_play,
                                  on_step=self.step,
                                  on_reset=self.reset,
                                  on_edit=self.back_to_setup)
        
        self.setup_panel.pack(fill="both", expand=True)

        # Columna derecha: mapa, estado y registro
        right = tk.Frame(self)
        right.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)
        self.map_view = MapView(right)
        self.map_view.pack(fill="both", expand=True)
        self.map_view.bind("<Button-1>", self.on_left_click)
        for button in ("<Button-2>", "<Button-3>", "<Control-Button-1>"):
            self.map_view.bind(button, self.on_right_click)   # clic derecho 
        self.status = tk.Label(right, text="", anchor="w")
        self.status.pack(fill="x", pady=(6, 6))
        self.log_panel = LogPanel(right)
        self.log_panel.pack(fill="x")
        self.log_panel.append([f"[carga] {i.file}:{i.line} {i.message}" for i in catalog.issues]
                      or ["[carga] Todo se cargó sin errores."])

        self.protocol("WM_DELETE_WINDOW", self.on_close)

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
        if not self.setup_world.in_bounds(x, y):
            return

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
        self._events_shown = 0
        self.log_panel.append(["── Nueva simulación ──"])
        self.setup_panel.pack_forget()
        self.run_panel.pack(fill="both", expand=True)
        self.refresh()

    # Fase de ejecución 

    def toggle_play(self)-> None:
        if self.running:
            self.pause()
        else:
            self.running= True
            self._loop()

    def _loop(self) -> None:
        """Un tick y se vuelve a programar. Tkinter lo llama cada delay_ms"""
        self._after_id= None
        if not self.running:
            return
        self.sim.tick()
        if self.sim.is_over:
            self.running = False
        else:
            self._after_id= self.after(self.run_panel.delay_ms, self._loop)
        self.refresh()

    def pause(self)-> None:
        self.running = False
        if self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None
        self.refresh()

    def step(self) -> None:
        self.pause()
        if not self.sim.is_over:
            self.sim.tick()
        self.refresh()


    def reset(self) -> None:
        self.pause()
        self.sim.reset()
        self._events_shown = 0 
        self.log_panel.append(["── Nueva simulación ──"])
        self.refresh()

    def back_to_setup(self) -> None:
        self.pause()
        self.sim = None
        self.run_panel.pack_forget()
        self.setup_panel.pack(fill="both", expand=True)
        self.refresh()

    def on_close(self)-> None:
        self.pause()
        self.destroy()

    # Dibujo

    def refresh(self) -> None:
        """Redibuja leyendo el mundo de la fase actual."""
        world = self.sim.world if self.sim else self.setup_world
        if world is None:
            return
        self.map_view.draw(world)
        alive = len(world.alive_creatures())
        if not self.sim:
            self.show_message(f"Preparación · {alive} criaturas colocadas")
            return
        new_events = self.sim.events_since(self._events_shown)
        self._events_shown += len(new_events)
        self.log_panel.append([f"[{e.tick}] {e.message}" for e in new_events])
        self.run_panel.show_state(self.running, self.sim.is_over)
        state = "Terminada" if self.sim.is_over else ("En marcha" if self.running else "En pausa")
        self.show_message(f"Tick {self.sim.tick_count} · {alive} vivas · {state}")


    def show_message(self, text: str) -> None:
        self.status.config(text=text)