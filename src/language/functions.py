from src.language.constants import WORLD_CONSTANTS
from src.world.creature import Creature
from src.world.world import World


def see(ctx,x:int,y:int)->int:
        creature, world = ctx.creature, ctx.world
        if world.chebyshev_distance(creature.x,creature.y,x,y)>creature.vision:
            return WORLD_CONSTANTS["NONE"]
        cell=world.get_cell(x,y)
        if cell is None:
            return WORLD_CONSTANTS["OBJECT"]
        if cell.creature: 
            if cell.creature.faction==creature.faction:
                return WORLD_CONSTANTS["ALLY"]
            return WORLD_CONSTANTS["ENEMY"]
        if cell.object:
            return WORLD_CONSTANTS["OBJECT"]
        return WORLD_CONSTANTS["GROUND"]

def name(ctx,x:int,y:int)->str:
    creature, world = ctx.creature, ctx.world
    if world.chebyshev_distance(creature.x,creature.y,x,y)>creature.vision:
        return ""
    cell=world.get_cell(x,y)
    if cell is None:
        return ""
    if cell.creature: 
        return cell.creature.species
    if cell.object:
        return cell.object.name
    return cell.terrain.name

FUNCTIONS= {"see": see, "name": name}

