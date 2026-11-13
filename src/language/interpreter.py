import random as _random_mod
from src.language.perceptions import snapshot
from src.world.world import World
from src.world.creature import Creature
from src.language.context import ExecutionContext

class Interpreter:
    def __init__(self,world:World,seed:int=42):
        self.world=world
        self.rng=_random_mod.Random(seed)

    def run_turn(self, creature:Creature):
        if not creature.alive:
            return
        if creature.wait_remaining>0:
            creature.wait_remaining-=1
            return
        program = creature.program
        ctx=ExecutionContext(creature, self.world, self.rng, program, ip=creature.instruction_pointer)

        ctx.perceptions= snapshot(creature,self.world,self.rng)

        while not ctx.turn_over and ctx.lines_executed<100 and creature.alive:
            if ctx.ip>=len(program.instructions):
                ctx.ip = program.labels["start"]
            inst=program.instructions[ctx.ip]
            ctx.line=inst.line_number
            ctx.lines_executed+=1
            inst.execute(ctx)
        creature.instruction_pointer=ctx.ip