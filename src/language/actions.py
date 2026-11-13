from abc import ABC, abstractclassmethod
from typing import List, Any
from src.world.world import World
from src.world.creature import Creature
from src.language.errors import InstinctRuntimeError

class Action(ABC):
    consumes_turn:bool=True

    @abstractclassmethod
    def execute(self,creature:Creature, world:World, args:List[Any])->None:
        pass

class WaitAction(Action):
    def execute(self, creature, world, args):
        num=_check_int(args[0])
        n=max(1,num)
        creature.wait_remaining=n-1 # -1 porque este turno ya cuenta

class MoveAction(Action):
    def execute(self, creature, world, args):
        
        dx,dy,speed=_check_int(args[0]),_check_int(args[1]),_check_int(args[2])
        if dx not in (-1,0,1) or dy not in (-1,0,1):
            raise InstinctRuntimeError("dx y dy solo pueden ser (-1, 0, 1)",0)
        world.move_creature(creature, dx, dy, speed)

class AttackAction(Action):
    def execute(self, creature, world, args):
        dx,dy,damage=_check_int(args[0]),_check_int(args[1]),_check_int(args[2])
        if dx not in (-1,0,1) or dy not in (-1,0,1):
            return
        _strike(creature, world, dx,dy,damage)

class ConsumeAction(Action):
    def execute(self, creature, world, args):
        dx,dy,damage,heal=_check_int(args[0]),_check_int(args[1]),_check_int(args[2]),_check_int(args[3])
        if dx not in (-1,0,1) or dy not in (-1,0,1):
            return 
        _strike(creature, world, dx, dy, damage)
        creature.health+=heal

class ReproduceAction(Action):
    def execute(self, creature, world, args):
        dx, dy, health_cost=_check_int(args[0]),_check_int(args[1]),_check_int(args[2])
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
    def execute(self, creature, world, args: List[Any]):
        text=str(args[0])
        # 1. Guardar para que otras criaturas lo escuchen  
        world.pending_roars.append((creature.x,creature.y,text)) 
        # 2. Registrar en los logs de la app
        world.add_event(f"📢 {creature.species} RUGIÓ: \"{text}\"")

class SayAction(Action):
    consumes_turn=False
    def execute(self, creature, world, args: List[Any]):
        text = str(args[0])
        # Registrar en los logs de la app
        world.add_event(f"💬 {creature.species} dice: \"{text}\"")


# FUNCIONES AUXILIARES DE VALIDACION Y COMBATE 

def _check_int(val: Any) -> int:
    """Verificar que el argumento sea un entero """
    if not isinstance(val,int) or isinstance(val,bool):
        raise TypeError(f"El argumento '{val}' debe ser un entero, no '{type(val).__name__}'")
    return val 

def _check_direction(dx:int, dy:int)-> None:
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        raise ValueError(f"Las direcciones dx y dy deben estar en {{-1, 0, 1}}, se obtuvo ({dx}, {dy})")

def _strike(creature: Creature, world: World, dx:int, dy:int, damage: int)->None:
    """
    Lógica compartida para attack y consume
    - Con (0, 0) ataca unicamente al terreno bajo la propia criatura
    - Con (dx, dy) != (0, 0) golpea a la casilla adyacente. Si hay criatura pierde vida,
      si hay objeto pierde reserva, y si solo hay terreno, este pierde reserva.
    - Fuera del mapa: no hace nada
    """
    if dx==0 and dy==0:
        cell=world.get_cell(creature.x,creature.y)
        if cell:
            cell.terrain.take_damage(damage)
        return 

    # Casillas adyacentes a distancia 1
    target=world.get_target_cell(creature, dx, dy)
    if target is None: 
        return 

    if target.creature:
        target.creature.health -= damage
        if target.creature.health <= 0:
            world.remove_creature(target.creature)
    elif target.object:
        target.object.take_damage(damage)
    else:
        target.terrain.take_damage(damage)

ACTION_REGISTRY={
    "wait": WaitAction(),
    "move": MoveAction(),
    "attack": AttackAction(),
    "consume": ConsumeAction(),
    "reproduce": ReproduceAction(),
    "roar": RoarAction(),
    "say": SayAction(),
}   