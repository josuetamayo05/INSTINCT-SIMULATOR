import copy
from src.world.world import World
from src.language.interpreter import Interpreter
from src.language.errors import InstinctRuntimeError


class Simulation:
    """Ejecuta el mundo tick a tick. La interfaz solo lee su estado
    (world, tick, is_over, events_since) y llama a tick() / reset()."""

    def __init__(self, setup_world: World, seed: int = 42):
        self.seed = seed
        self._template = copy.deepcopy(setup_world)   # foto del mundo preparado
        self.reset()

    def reset(self) -> None:
        """Vuelve al mundo tal como estaba al crear la simulación."""
        self.world = copy.deepcopy(self._template)
        self.interpreter = Interpreter(self.world, self.seed)

    def tick(self) -> None:
        alive = self.world.alive_creatures()
        self.interpreter.rng.shuffle(alive)
        for creature in alive:
            if not creature.alive:
                continue
            try:
                self.interpreter.run_turn(creature)
            except InstinctRuntimeError as e:
                self.world.add_event(f"{creature.species}: {e}")
                self.world.remove_creature(creature)
        self.world.end_of_tick()

    # Lectura para la interfaz

    @property
    def tick_count(self) -> int:
        return self.world.tick_count

    @property
    def is_over(self) -> bool:
        return not self.world.alive_creatures()

    def events_since(self, index: int):
        """Eventos nuevos desde la posición index (para el panel de logs)."""
        return self.world.events[index:]
