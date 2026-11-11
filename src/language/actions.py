from abc import ABC, abstractclassmethod
from typing import List, Any
from src.world.world import World
from src.world.creature import Creature

class Action(ABC):
    consumes_turn:bool=True

    @abstractclassmethod
    def execute(self,creature:Creature, world:World, args:List[Any])->None:
        pass

class WaitAction(Action):
    def execute(self, creature, world, args):
        n=max(1,int(args[0]))
        creature.wait_remaining=n-1 # -1 porque este turno ya cuenta

class MoveAction(Action):
    def execute(self, creature, world, args):
        dx,dy,speed=int(args[0]),int(args[1]),int(args[2])
        if dx not in (-1,0,1) or dy not in (-1,0,1):
            from src.language.errors import InstinctRuntimeError
            raise InstinctRuntimeError("dx y dy solo pueden ser (-1, 0, 1)",0)
        world.move_creature(creature, dx, dy, speed)

class AttackAction(Action):
    def execute(self, creature, world, args):
        dx,dy,damage=int(args[0]),int(args[1]),int(args[2])
        if dx not in (-1,0,1) or dy not in (-1,0,1):
            return
        target=world.get_target_cell(creature,dx,dy)
        if target is None:
            return
        if target.creature:
            target.creature.health-=damage
            if target.creature.health<=0:
                world.remove_creature(target.creature)
        elif target.object:
            target.object.take_damage(damage)
        else:
            target.terrain.take_damage(damage)

class ConsumeAction(Action):
    def execute(self, creature, world, args):
        dx,dy,damage,heal=int(args[0]),int(args[1]),int(args[2]),int(args[3])
        if dx not in (-1,0,1) or dy not in (-1,0,1):
            return 
        target=world.get_target_cell(creature, dx, dy)
        if target is None: return
        if target.creature:
            target.creature.health-=damage
            if target.creature.health<=0:
                world.remove_creature(target.creature)
        elif target.object:
            target.object.take_damage(damage)
        else:
            target.terrain.take_damage(damage)
        creature.health+=heal

class ReproduceAction(Action):
    def execute(self, creature, world, args):
        dx, dy, health_cost=int(args[0]),int(args[1]),int(args[2])
        if dx not in (-1,0,1) or dy not in (-1,0,1):
            return
        if creature.health <= health_cost:
            return
        target=world.get_target_cell(creature, dx, dy)
        if target is None or not target.is_walkable():
            return
        creature.health-=health_cost
        baby=Creature(
            species=creature.species,
            faction=creature.faction,
            health=health_cost,
            vision=creature.vision,
            lifespan=creature.lifespan,
            program=creature.program,
        )
        world.place_creature(baby, creature.x+dx,creature.y+dy)

class RoarAction(Action):
    def execute(self, creature, world, args):
        text=str(args[0])
        world.roar_buffer.append((creature.x,creature.y,text)) 

class SayAction(Action):
    consumes_turn=False
    def execute(self, creature, world, args):
        pass 

ACTION_REGISTRY={
    "wait": WaitAction(),
    "move": MoveAction(),
    "attack": AttackAction(),
    "consume": ConsumeAction(),
    "reproduce": ReproduceAction(),
    "roar": RoarAction(),
    "say": SayAction(),
}   