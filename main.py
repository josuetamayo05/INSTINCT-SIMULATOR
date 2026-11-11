from src.world.world import World
from src.world.terrain import Terrain
from src.world.creature import Creature
from src.language.interpreter import Interpreter
from src.loaders.creature_loader import load_creature

world = World(10, 10, Terrain("Grass", ".", 100, 2))
prog = load_creature("data/creatures/hobbit.ins")
c = Creature("Hobbit", "shire", 60, 5, 300, program=prog)
world.place_creature(c, 3, 3)
interp = Interpreter(world, seed=1)
for t in range(8):
    interp.run_turn(c)
    print(t, (c.x, c.y), c.health, "ip =", c.instruction_pointer)