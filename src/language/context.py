from dataclasses import dataclass

@dataclass
class ExecutionContext:
    """Contexto de ejecucion para la interpretacion de un programa Instinct"""
    creature: "Creature" 
    world: "World"
    rng: "random.Random"
    program: "CompiledProgram"
    ip: int=0
    line:int=0
    lines_executed:int=0
    turn_over: bool = False