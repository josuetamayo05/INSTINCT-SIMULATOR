from dataclasses import dataclass, field
from typing import Dict, Any,Optional
from src.world.entity import Entity

@dataclass
class Creature(Entity):
    species:str
    faction:str
    health:int
    vision:int
    lifespan:int
    age:int=0
    x:int=0
    y:int=0
    alive:bool=True
    variables: Dict[str, Any]=field(default_factory=dict)
    program:Any=None    # Programa de comportamiento del criatura
    instruction_pointer:int=0   # Indice de la proxima instruccion a ejecutar
    wait_remaining:int=0    # Turnos restante de espera antes de ejecutar la siguiente instruccion
    lines_executed:int=0    # Contador de lineas en el turno actual

    def is_dead(self)->bool:
        return self.health <= 0 or self.age >= self.lifespan or not self.alive

    def end_of_tick(self):
        self.health -= 1
        self.age += 1
        

    def take_damage(self, amount: int) -> int:
        self.health -= amount
        return amount

    def is_depleted(self):
        return self.health<=0
    
    @classmethod
    def from_program(cls, program):
        return cls(program.creature_name, program.faction, program.health, program.vision, program.lifespan, program=program)
