from dataclasses import dataclass
from src.world.entity import ReserveEntity
@dataclass
class Terrain(ReserveEntity):
    regen: int

    def regenerate(self):
        self.reserve = min(self.resource_max, self.reserve + self.regen)

    def copy(self) -> "Terrain":
        return Terrain(self.name, self.char, self.resource_max, self.regen)