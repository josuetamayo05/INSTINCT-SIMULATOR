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