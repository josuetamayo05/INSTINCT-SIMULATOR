from dataclasses import dataclass, field
from typing import Dict, Any,Optional

@dataclass
class Creature:
    species:str
    faction:str
    health:int
    vision:int
    lifespan:int
    age:int=0
    x:int=0
    y:int=0
    age:int=0
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
        if self.is_dead():
            self.alive = False
