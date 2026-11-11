import random
from src.world.world import World
from src.world.terrain import Terrain
from src.world.creature import Creature
from src.language.context import ExecutionContext
from src.language.ast_nodes import *

world = World(10, 10, Terrain("Grass", ".", 100, 2))
c = Creature("Hobbit", "shire", 60, 5, 300, program=None)
world.place_creature(c, 3, 3)
ctx = ExecutionContext(c, world, random.Random(1), None, line=7)

print(BinaryOp("+", LiteralInt(2), BinaryOp("*", LiteralInt(3), LiteralInt(4))).evaluate(ctx))  # 14
print(VariableRef("health").evaluate(ctx))                                                      # 60
# print(BinaryOp("==", LiteralInt(1), LiteralString("a")).evaluate(ctx))  # error, línea 7
print(BinaryOp("/", LiteralInt(1), LiteralInt(0)).evaluate(ctx))        # error, línea 7