from dataclasses import dataclass
from src.world.entity import ReserveEntity
@dataclass
class WorldObject(ReserveEntity):
    def copy(self)-> "WorldObject":
        return WorldObject(self.name, self.char, self.resource_max)