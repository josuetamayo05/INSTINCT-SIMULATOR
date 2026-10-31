from typing import List, Optional
from src.world.creature import Creature
from src.world.world_object import WorldObject
from src.world.terrain import Terrain

class Cell:
    def __init__(self, terrain: Terrain):
        self.terrain = terrain
        self.object: Optional[WorldObject] = None
        self.creature: Optional[Creature] = []

    def is_walkable(self) -> bool:
        return self.object is None and self.creature is None

    def has_object(self) -> bool:
        return self.object is not None

    def has_creature(self) -> bool:
        return self.creature is not None

    