from abc import ABC, abstractmethod
from dataclasses import dataclass, field

class Entity(ABC):
    """Todo lo que ocupa una casilla y puede recibir un golpe"""

    @abstractmethod
    def take_damage(self, amount: int) -> int:
        """Aplica el golpe y devuelve cuanto se quito realmente"""

    @abstractmethod
    def is_depleted(self) -> bool:
        """Se quedo sin reserva o sin vida?"""

@dataclass
class ReserveEntity(Entity):
    """Terreno u objeto: un golpe le quita la reserva, nunca por debajo de 0"""
    name: str
    char:str
    resource_max: int
    reserve: int = field(init=False)

    def __post_init__(self):
        self.reserve = self.resource_max

    def take_damage(self, amount: int) -> int:
        actual = min(amount, self.reserve)
        self.reserve-= actual
        return actual

    def is_depleted(self)->bool:
        return self.reserve<=0