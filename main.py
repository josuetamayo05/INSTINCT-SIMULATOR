vscode_lsp_terminal_prompt_tracker= {}
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
for i in cat.issues: print(f"[LOAD] {i.file}:{i.line} {i.message}")


world = copy.deepcopy(cat.maps["Plain with rocks"])
world.place_creature(Creature.from_program(cat.species["Hobbit"]), 2, 2)
world.place_creature(Creature.from_program(cat.species["Uruk"]), 12, 4)
sim = Simulation(world, seed=1)
for t in range(10):
    sim.tick()
    print(f"--- tick {t} ---\n{render(world)}")
    
name = "Plain with rocks"
if name not in cat.maps:
    raise SystemExit(f"El mapa '{name}' no se cargó. Revisa los errores de arriba.")