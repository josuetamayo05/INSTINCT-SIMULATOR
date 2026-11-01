from src.language.lexer import Lexer
from src.language.tokens import TokenType
from src.world.creature import Creature 
from src.world.terrain import Terrain
from src.world.world_object import WorldObject as Object

Grass=Terrain("Grass",".",100,2)
Rock=Object("Rock","#", 100)

Hobbit=Creature("Hobbit","shire",60,5,300)

sample_code="""
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

def test_lexer():
    lexer = Lexer(sample_code)
    tokens = lexer.tokenize()
    print("--- TOKENS GENERADOS ---")
    for t in tokens:
        print(t)
    print("------------------------")
    print(f"Total de tokens: {len(tokens)}")

if __name__ == "__main__":
    test_lexer()