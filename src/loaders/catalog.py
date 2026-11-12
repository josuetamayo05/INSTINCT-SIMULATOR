from typing import Dict, List
from dataclasses import dataclass
from src.world.terrain import Terrain
from src.world.creature import Creature
from src.language.parser import CompiledProgram
from src.world.world_object import WorldObject
from src.world.world import World

@dataclass
class LoadIssue:
    file: str
    line: int
    message: str

class Catalog:
    def __init__(self):
        self.terrains: Dict[str,Terrain] = {}
        self.objects: Dict[str, WorldObject] = {}
        self.maps: Dict[str, World] = {}
        self.species: Dict[str, CompiledProgram] = {}
        self.issues: List[LoadIssue] = []

    def load_all(self,base_dir="data"):
        pass