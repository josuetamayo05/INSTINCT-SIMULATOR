from typing import List
from src.world.world import World
from src.language.interpreter import Interpreter
from src.world.creature import Creature
from src.language.errors import InstinctRuntimeError
class Simulation:
    def __init__(self, world: World, seed: int = 42):
        self.world = world
        self.interpreter = Interpreter(world, seed)
        self.running=False

    def tick(self):
        alive=self.world.alive_creatures()
        self.interpreter.rng.shuffle(alive)

        # Limpiar buffer de rugidos del tick anterior
        self.world.roar_buffer.clear()

        for creature in alive:
            if not creature.alive:
                continue
            try:
                self.interpreter.run_turn(creature)
            except InstinctRuntimeError as e:
                self.world.events.append(f"[tick {self.world.tick_count}] {creature.species}: {e}")
                self.world.remove_creature(creature)

        self.world.end_of_tick()

    def run(self, max_ticks: int=100):
        self.running=True
        for t in range(max_ticks):
            if not self.running:
                break
            alive=self.world.alive_creatures()
            if not alive:
                print(f"Todos los seres vivos han muerto en el tick {t}.")
                break
            self.tick()
            if t%10==0:
                factions={}
                for creature in alive:
                    factions[creature.faction]=factions.get(creature.faction,0)+1
                print(f"Tick {t}: {len(alive)} criaturas vivas. Facciones: {factions}")