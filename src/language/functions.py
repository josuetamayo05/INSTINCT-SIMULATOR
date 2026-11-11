from src.language.constants import WORLD_CONSTANTS
from src.world.creature import Creature

def _fn_see(self,creature:Creature,x:int,y:int)->int:
        if self.world.chebyshev_distance(creature.x,creature.y,x,y)>creature.vision:
            return WORLD_CONSTANTS["NONE"]
        cell=self.world.get_cell(x,y)
        if cell is None:
            return WORLD_CONSTANTS["OBJECT"]
        if cell.creature: 
            if cell.creature.faction==creature.faction:
                return WORLD_CONSTANTS["ALLY"]
            return WORLD_CONSTANTS["ENEMY"]
        if cell.object:
            return WORLD_CONSTANTS["OBJECT"]
        return WORLD_CONSTANTS["GROUND"]

def _fn_name(self,creature:Creature,x:int,y:int)->str:
    if self.world.chebyshev_distance(creature.x,creature.y,x,y)>creature.vision:
        return ""
    cell=self.world.get_cell(x,y)
    if cell is None:
        return "UNKNOWN"
    if cell.creature: 
        return cell.creature.species
    if cell.object:
        return cell.object.name
    return cell.terrain.name