from src.world.terrain import Terrain
from src.language.errors import CompileError
from src.loaders.common import parse_int, parse_key_value

def load_terrain(filepath:str)-> Terrain:
    name=char=None
    resource_max=regen=None

    with open(filepath, "r", encoding="utf-8") as f:
        for i, raw in enumerate(f,1):
            kv = parse_key_value(raw,i)
            if kv is None: 
                continue
            key, val = kv
            if key == "terrain":
                name=val
            elif key == "char":
                if len(val) != 1: 
                    raise CompileError("char debe ser un solo carácter", i)
                char = val
            elif key == "resource_max":
                resource_max = parse_int(val, key, i)
                if resource_max <= 0:
                    raise CompileError("resource_max debe ser mayor que 0", i)
            elif key == "regen":
                regen = parse_int(val, key, i)
                if regen < 0:
                    raise CompileError("regen no puede ser negativo", i)
            else:
                raise CompileError(f"Clave desconocida '{key}'", i)

    if name is None or char is None or resource_max is None or regen is None:
        raise CompileError("Terreno incompleto: faltan terrain, char, resource o regen", 1)

    return Terrain(name, char, resource_max, regen)