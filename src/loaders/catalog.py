from typing import Dict, List
from dataclasses import dataclass
from src.world.terrain import Terrain
from src.world.creature import Creature
from src.language.parser import CompiledProgram
from src.world.world_object import WorldObject
from src.world.world import World
import os
from src.language.errors import CompileError, LexerError
from src.loaders.creature_loader import load_creature
from src.loaders.terrain_loader import load_terrain
from src.loaders.map_loader import load_map
from src.loaders.object_loader import load_object

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

    def load_all(self,base="data"):
        for p, t in self._each(f"{base}/terrains",".te",load_terrain):
            self._register(self.terrains, t.name, t, p, char=t.char)
        for p, o in self._each(f"{base}/objects",".ob", load_object):
            self._register(self.objects, o.name, o, p, char=o.char)
        for p, (name, w) in self._each(f"{base}/maps",".map", lambda f: load_map(f, self.terrains, self.objects)):
            self._register(self.maps, name, w, p)
        for p, prog in self._each(f"{base}/creatures", ".ins", load_creature):
            self._register(self.species, prog.creature_name, prog, p)

    def _each(self, folder, ext, loader):
        if not os.path.isdir(folder):
            return
        for fname in sorted(os.listdir(folder)):
            if not fname.endswith(ext):
                continue
            path=os.path.join(folder, fname)
            try:
                yield path, loader(path)
            except (CompileError, LexerError) as e:
                self.issues.append(LoadIssue(path, e.line, e.message))
            except (OSError, UnicodeDecodeError) as e:
                self.issues.append(LoadIssue(path, 0, f"No se pudo leer el archivo: {e}"))

    def _register(self, table, name, item, path, char=None):
        if name in table:
            self.issues.append(LoadIssue(path, 1, f"El nombre '{name}' ya está guardado"))
        elif char is not None and any(x.char == char for x in [*self.terrains.values(),*self.objects.values()]):
            self.issues.append(LoadIssue(path, 1, f"El char '{char}' ya lo usa otro elemento"))
        else: 
            table[name] = item
        