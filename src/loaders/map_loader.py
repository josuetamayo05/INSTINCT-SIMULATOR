from typing import Dict, Tuple
from src.world.world_object import WorldObject
from src.world.world import World
from src.world.terrain import Terrain
from src.language.errors import CompileError

def load_map(filepath:str, terrains: Dict[str,Terrain],objects:Dict[str,WorldObject])->Tuple[str,World]:
    with open(filepath,"r",encoding="utf-8") as f:
        lines=[l.rstrip("\n") for l in f.readlines()]

    if not lines:
        raise CompileError("Mapa vacio", 1)

    map_name=lines[0].strip()
    grid_lines=[l for l in lines[1:] if l.strip()]

    if not grid_lines:
        raise CompileError("Mapa sin filas",1)

    height=len(grid_lines)
    width=len(grid_lines[0])

    # Construir lookup char a terreno/objeto
    char_to_terrain={t.char: t for t in terrains.values()}
    char_to_object={o.char: o for o in objects.values()}

    default_terrain=list(terrains.values())[0] if terrains else Terrain("Grass",".",100,2)
    world = World(width,height,default_terrain)

    for y, row in enumerate(grid_lines):
        for x, ch in enumerate(row):
            if len(row) != width:
                raise CompileError(f"La fila mide {len(row)} y debería medir {width}", y+2)
            
            if ch in char_to_object:
                cell=world.get_cell(x,y)
                cell.object= char_to_object[ch].copy() if char_to_object[ch].copy() else WorldObject(
                    char_to_object[ch].name, ch, char_to_object[ch].resource_max
                )

            elif ch in char_to_terrain:
                world.grid[y][x].terrain=char_to_terrain[ch].copy()
            elif ch==' ':
                continue
            else: raise CompileError(f"Caracter desconocido '{ch}' en el mapa",y+2)
    
    return map_name,world