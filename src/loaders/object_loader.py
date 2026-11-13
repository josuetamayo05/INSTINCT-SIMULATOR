from src.world.world_object import WorldObject
from src.language.errors import CompileError
from src.loaders.common import parse_key_value, parse_int

def load_object(filepath: str)-> WorldObject:
    name=char=None
    resource_max=None

    with open(filepath, "r", encoding="utf-8") as f:
        for i,raw in enumerate(f,1):
            kv= parse_key_value(raw, i)
            if kv is None:
                continue
            key, val = kv
            if key=="object":
                name=val
            elif key=="char":
                if len(val)!=1:
                    raise CompileError("char must be a single character",i)
                char = val
            elif key=="resource_max":
                resource_max=parse_int(val,key,i)
                if resource_max <= 0:
                    raise CompileError("resource_max must be greater than 0",i)
            else:
                raise CompileError(f"Clave desconocida '{key}'", i)

    if name is None or char is None or resource_max is None:
        raise CompileError("Objeto incompleto: faltan object, char o resource_max",1)
    
    return WorldObject(name, char, resource_max)