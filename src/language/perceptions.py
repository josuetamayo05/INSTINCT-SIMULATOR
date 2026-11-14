from abc import ABC, abstractmethod
from src.world.world import World
from src.world.creature import Creature
import random as _random
from typing import Any

def _direction(a:int, b:int)->int:
    """Step in {-1, 0, 1} to go from a to b."""
    return 0 if a==b else (1 if b>a else -1)

def _find_nearest(creature:Creature, world: World, filter_fn):
    best_dist=float("inf")
    best_dx,best_dy=0,0
    for c in world.alive_creatures():
        if c is creature:
            continue
        if not filter_fn(c,creature):
            continue
        d=world.chebyshev_distance(creature.x,creature.y,c.x,c.y)
        if d<=creature.vision and d<best_dist:
            best_dist=d
            dx=0 if c.x == creature.x else (1 if c.x > creature.x else-1)
            dy=0 if c.y == creature.y else (1 if c.y > creature.y else-1)
            best_dx,best_dy=dx,dy
    if best_dist==float("inf"):
        return -1,0,0
    return best_dist, best_dx, best_dy

def _find_nearest_object(creature:Creature, world:World):
    best_dist=float("inf")
    best_dx,best_dy=0,0
    for y in range(world.height):
        for x in range(world.width):
            cell=world.grid[y][x]
            if cell.object:
                d=world.chebyshev_distance(creature.x,creature.y,x,y)
                if d<=creature.vision and d<best_dist:
                    best_dist=d
                    best_dx=0 if x==creature.x else (1 if x>creature.x else -1)
                    best_dy=0 if y==creature.y else (1 if y>creature.y else -1)

    if best_dist==float("inf"):
        return -1,0,0
    return best_dist, best_dx, best_dy

def _count_creatures(creature:Creature, world:World, filter_fn, only_visible:bool)-> int:
    count = 0
    for c in world.alive_creatures():
        if c is creature or not filter_fn(c,creature):
            continue
        if only_visible and world.chebyshev_distance(creature.x, creature.y, c.x, c.y)>creature.vision:
            continue
        count+=1
    return count

def _visible_roars(creature:Creature, world:World):
    """Texts of the roars from the previous tick of the vision, in order"""
    return [text for rx, ry, text in world.roar_buffer 
            if world.chebyshev_distance(creature.x,creature.y,rx,ry)<= creature.vision]

def _same_faction(c, me):
    return c.faction == me.faction

def _other_faction(c, me):
    return c.faction != me.faction

def _anyone(c, me): return True

class Perception(ABC):
    live = False
    @abstractmethod
    def read(self, creature, world, rng) -> Any:
        """Calcula el valor de la percepcion para esta criatura ahora """

class CreatureAttr(Perception):
    def __init__(self, attr:str):
        self.attr = attr
    def read(self, creature, world, rng):
        return getattr(creature, self.attr)

class WorldAttr(Perception):
    def __init__(self, attr:str):
        self.attr=attr
    def read(self, creature, world, rng):
        return getattr(world, self.attr)

class Count(Perception):
    """Cuenta criaturas que cumplen un filtro, en todo el mapa o solo en lav vision"""
    def __init__(self, filter_fn, only_visible: bool):
        self.filter_fn = filter_fn
        self.only_visible = only_visible 
         
    def read(self, creature, world, rng):
        return _count_creatures(creature, world, self.filter_fn, self.only_visible)
class Nearest(Perception):
    """Una componente (0=dist, 1=dx, 2=dy) de la busqueda del mas cercano"""
    def __init__(self, search, component):
        self.search=search
        self.component=component
        
    def read(self, creature, world, rng):
        return self.search(creature,world)[self.component]

class TerrainHere(Perception):
    """Atributo del terreno bajo la criatura (name, reserve)"""
    def __init__(self, attr: str, default):
        self.attr = attr
        self.default = default
    def read(self, creature, world, rng):
        cell = world.get_cell(creature.x, creature.y)
        return getattr(cell.terrain, self.attr) if cell else self.default

class ObjectsNear(Perception):
    def read(self, creature, world, rng):
        count = 0
        for y in range(world.height):
            for x in range(world.width):
                if world.grid[y][x].object and \
                   world.chebyshev_distance(creature.x, creature.y, x, y) <= creature.vision:
                    count += 1
        return count

class RandomNumber(Perception):
    live = True
    def read(self, creature, world, rng):
        return rng.randint(0, 99)

class RoarsNear(Perception):
    def read(self, creature, world, rng):
        return len(_visible_roars(creature, world))

class LastRoar(Perception):
    def read(self, creature, world, rng):
        roars = _visible_roars(creature, world)
        return roars[-1] if roars else ""
    

def _nearest_creature(filter_fn):
    """Función de búsqueda con el filtro ya fijado"""
    return lambda creature, world: _find_nearest(creature, world, filter_fn)

def _nearest_group(prefix: str, search) -> dict:
    """Creates<prefix>_dist,<prefix>_dx and<prefix>_dy."""
    return {f"{prefix}_{suffix}": Nearest(search, i)
            for i, suffix in enumerate(("dist", "dx", "dy"))}
    
PERCEPTIONS = {
    # Propias
    **{attr: CreatureAttr(attr) for attr in
       ("health", "age", "lifespan", "vision", "species", "faction", "x", "y")},
    "terrain_here": TerrainHere("name", ""),
    "reserve_here": TerrainHere("reserve", 0),
    # Del mundo
    "width":  WorldAttr("width"),
    "height": WorldAttr("height"),
    "tick":   WorldAttr("tick_count"),
    "total_creatures": Count(_anyone, only_visible=False),
    "total_allies":    Count(_same_faction, only_visible=False),
    "total_enemies":   Count(_other_faction, only_visible=False),
    "random": RandomNumber(),
    # Del entorno cercano
    "allies_near":  Count(_same_faction, only_visible=True),
    "enemies_near": Count(_other_faction, only_visible=True),
    "objects_near": ObjectsNear(),
    **_nearest_group("enemy",  _nearest_creature(_other_faction)),
    **_nearest_group("ally",   _nearest_creature(_same_faction)),
    **_nearest_group("object", _find_nearest_object),
    "roars_near": RoarsNear(),
    "last_roar":  LastRoar(),
}

# Unica fuente de verdad, el parser la usa para prohibir asignaciones 
READONLY_PERCEPTIONS = frozenset(PERCEPTIONS)

def snapshot(creature, world, rng ) -> dict:
    """Values of all collections at the start of the shift"""
    return {name: p.read(creature,world,rng) for name, p in PERCEPTIONS.items() if not p.live}
