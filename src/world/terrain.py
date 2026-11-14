from dataclasses import dataclass
from src.world.entity import ReserveEntity
@dataclass
class Terrain(ReserveEntity):
    regen: int

    def __post_init__(self):
        self.reserve = self.resource_max

    def regenerate(self):
        self.reserve = min(self.resource_max, self.reserve + self.regen)

    def copy(self)->"Terrain":
        t=Terrain(self.name, self.char, self.resource_max, self.regen, self.reserve)
        t.reserve=self.resource_max
        return t