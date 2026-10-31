from src.world.world_object import WorldObject
from src.language.errors import CompileError

def load_object(filepath: str)-> WorldObject:
    name=char=None
    resource_max=None

    with open(filepath, "r", encoding="utf-8") as f:
        for i,line in enumerate(f,1):
            line=line.split("#")[0].strip()
            if not line:
                continue
        parts=line.split()
        if len(parts)!=2:
            raise CompileError(f"Linea invalida en objeto",i)
        key,val=parts[0],parts[1]
        if key=="object":
            name=val
        elif key=="char":
            char=val
        elif key=="resource_max":
            resource_max=int(val)

    if not all([name,char,resource_max is not None]):
        raise CompileError("Objeto incompleto",1)
    
    return WorldObject(name,char,resource_max)