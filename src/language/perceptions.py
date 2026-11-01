from typing import Any
from src.world.world import World
from src.world.creature import Creature
import random as _random

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
    return best_dist,best_dx,best_dy

def _count_near(creature:Creature, world: World, filter_fn)->int:
    count=0
    for c in world.alive_creatures():
        if c is creature: continue
        if filter_fn(c,creature) and world.chebyshev_distance(creature.x,creature.y,c.x,c.y)<=creature.vision:
            count+=1
    return count

def _count_objects_near(creature:Creature, world:World)->int:
    count=0
    for y in range(world.height):
        for x in range(world.width):
            if world.grid[y][x].object and world.chebyshev_distance(creature.x,creature.y,x,y)<=creature.vision:
                count+=1
    return count

def get_perception(name:str, creature: Creature, world:World, rng)->Any:
    cell=world.get_cell(creature.x,creature.y)

    if name == "health":
        return creature.health
    if name == "age":
        return creature.age
    if name == "lifespan":
        return creature.lifespan
    if name == "vision":
        return creature.vision
    if name == "species":
        return creature.species
    if name == "faction":
        return creature.faction
    if name == "x":
        return creature.x
    if name == "y":
        return creature.y
    if name=="terrain_here":
        return cell.terrain.name if cell else ""
    if name == "reserve_here":
        return cell.terrain.reserve if cell else 0
    if name == "width":
        return world.width
    if name == "height":
        return world.height
    if name == "tick":
        return world.tick_count
    if name == "total_creatures":
        return len(world.alive_creatures()) - 1
    if name == "total_allies":
        return _count_near(creature, world, lambda c, me: c.faction == me.faction)
    if name == "total_enemies":
        return _count_near(creature, world, lambda c, me: c.faction != me.faction)
    if name == "random":
        return rng.randint(0, 99)
    if name == "allies_near":
        return _count_near(creature, world, lambda c, me: c.faction == me.faction)
    if name == "enemies_near":
        return _count_near(creature, world, lambda c, me: c.faction != me.faction)
    if name == "objects_near":
        return _count_objects_near(creature, world)

    # enemigo mas cercano
    if name in ("enemy_dist","enemy_dx", "enemy_dy"):
        d, dx, dy = _find_nearest(creature, world, lambda c, me: c.faction != me.faction)
        return {"enemy_dist":d, "enemy_dx":dx, "enemy_dy":dy}[name]

    # Aliado mas cercano
    if name in ("ally_dist", "ally_dx", "ally_dy"):
        d, dx, dy = _find_nearest(creature, world, lambda c, me: c.faction == me.faction)
        return {"ally_dist": d, "ally_dx": dx, "ally_dy": dy}[name]

    # Objeto mas cercano
    if name in ("object_dist","object_dx","object_dy"):
        d, dx, dy = _find_nearest_object(creature,world)
        return {"object_dist": d, "object_dx":dx, "object_dy":dy}[name]

    if name=="roars_near":
        count=0
        for rx, ry, _ in world.roar_buffer:
            if world.chebyshev_distance(creature.x,creature.y,rx,ry)<=creature.vision:
                count+=1
            return count

    if name=="last_roar":
        for rx, ry, text in reversed(world.roar_buffer):
            if world.chebyshev_distance(creature.x,creature.y,rx,ry)<=creature.vision:
                return text
            return ""

    return None

    