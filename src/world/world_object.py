from dataclasses import dataclass
from src.world.entity import ReserveEntity
@dataclass
class WorldObject(ReserveEntity):

    def __post_init__(self):
        self.reserve = self.resource_max

    def copy(self)-> "WorldObject":
        return WorldObject(self.name, self.char, self.resource_max)