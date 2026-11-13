import copy
from src.loaders.catalog import Catalog
from src.simulation.simulation import Simulation
from src.world.creature import Creature

def render(world):
    out = []
    for row in world.grid:
        s = ""
        for cell in row:
            if cell.creature:   s += cell.creature.species[0]
            elif cell.object:   s += cell.object.char
            else:               s += cell.terrain.char
        out.append(s)
    return "\n".join(out)

cat = Catalog(); cat.load_all()
for i in cat.issues:
    print(f"[LOAD] {i.file}:{i.line} {i.message}")

setup = copy.deepcopy(cat.maps["Plain with rocks"])
setup.place_creature(Creature.from_program(cat.species["Hobbit"]), 2, 2)
setup.place_creature(Creature.from_program(cat.species["Uruk"]), 12, 4)

sim = Simulation(setup, seed=1)
for _ in range(10):
    sim.tick()
    print(f"--- tick {sim.tick_count} ---\n{render(sim.world)}")