from world.world import World
from simulation.simulation import Simulation
from world.creature import Creature
from world.terrain import Terrain
from language.lexer import Lexer
from language.parser import Parser

HOBBIT_CODE="""creature Hobbit
faction shire
health 60
vision 5
lifespan 300
start:
if enemy_dist >= 0 goto flee
if health > 45 and total_allies < 20 goto breed
if reserve_here > 0 and health < 80 goto second_breakfast
if ally_dist > 1 goto go_ally
wait(1)
goto start
flee:
say("they are taking us to Isengard")
move(-enemy_dx, -enemy_dy, 2)
goto start
second_breakfast:
consume(0, 0, 10, 10)
goto start
go_ally:
move(ally_dx, ally_dy, 1)
goto start
breed:
if see(x + 1, y) == GROUND goto breed_right
if see(x - 1, y) == GROUND goto breed_left
wait(1)
goto start
breed_right:
reproduce(1, 0, 20)
goto start
breed_left:
reproduce(-1, 0, 20)
goto start
"""

URUK_CODE="""creature Uruk
faction isengard
health 80
vision 4
lifespan 400
start:
if health<20 goto flee  
if enemy_dist>=0 goto hunt
if health>70 and allies_near<2 goto breed
wander:
move(random%3-1, random%3-1, 1)
goto start
bite:
consume(enemy_dx, enemy_dy, 15, 15)
goto start
hunt:
move(enemy_dx, enemy_dy, 2)
goto start
flee:
move(-enemy_dx, -enemy_dy, 3)
goto start
breed:
if see(x,y+1) != GROUND goto wander
reproduce(0, 1, 30)
goto start
"""

def test_simulation():
    print("Iniciando prueba de simulación...")
    # Crear mundo de pasto 20x20
    grass=Terrain("Grass", ".", 100, 2)
    world=World(20, 20, grass)

    # Compilar creaturas
    hobbit_prog=Parser(Lexer(HOBBIT_CODE).tokenize()).parse()
    uruk_prog=Parser(Lexer(URUK_CODE).tokenize()).parse()

    # Colocar hobbits
    for i in range(5):
        hobbit=Creature("Hobbit", "shire", 60, 5, 300, program=hobbit_prog)
        world.place_creature(hobbit, 2+i, 2)

    # Colocar uruks
    for i in range(3):
        uruk=Creature("Uruk", "isengard", 80, 6, 400, program=uruk_prog)
        world.place_creature(uruk, 15+i, 15)

    print(f"Mundo: {world.width}x{world.height}")
    print(f"Criaturas iniciales: {len(world.creatures)}")

    # Correr simulación
    sim=Simulation(world, seed=42)
    sim.run(max_ticks=50)

    print(f"\nCriaturas finales: {len(world.alive_creatures())}")
    for c in world.alive_creatures():
        print(f"  {c.species} ({c.faction}) en ({c.x},{c.y}) HP={c.health} edad={c.age}")
    print("\n✅ ¡Simulación completada!")

if __name__ == "__main__":
    test_simulation()