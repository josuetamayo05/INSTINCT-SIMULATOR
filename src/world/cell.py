from typing import List, Optional
from world.creature import Creature
from world.world_object import WorldObject
from world.terrain import Terrain

class Cell:
    def __init__(self, terrain: Terrain):
        self.terrain = terrain
        self.object: Optional[WorldObject] = None
        self.creature: Optional[Creature] = []

    def is_walkable(self) -> bool:
        return self.object is None and len(self.creature) == 0

    def has_object(self) -> bool:
        return self.object is not None

    def has_creature(self) -> bool:
        return len(self.creature) > 0

    