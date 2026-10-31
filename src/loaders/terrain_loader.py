from src.world.terrain import Terrain
from src.language.errors import CompileError

def load_terrain(filepath:str)-> Terrain:
    name=char=None
    resource_max=regen=None

    with open(filepath, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.split("#")[0].strip()
            if not line:
                continue
            parts=line.split()
            if len(parts) != 2:
                raise CompileError(f"Línea inválida en terreno")
            key, val=parts[0],parts[1]
            if key=="terrain":
                name=val
            elif key=="char":
                char=val
            elif key=="resource_max":
                resource_max=int(val)
            elif key=="regen":
                regen=int(val)

    if not all([name,char,resource_max is not None, regen is not None]):
        raise CompileError("Terreno incompleto",1)

    return Terrain(name,char,resource_max, regen)