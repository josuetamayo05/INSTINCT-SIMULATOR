from src.language.errors import CompileError

def parse_key_value(raw:str, line_no:int):
    """Returns (key, value) or None if the line is empty or is a comment"""
    text=raw.strip()
    if not text or text.startswith("#"):
        return None
    parts=text.split()
    # 'char #' is valid: the value is '#'. Only what comes after the value is a comment.
    if len(parts)<2 or (len(parts)>2 and not parts[2].startswith("#")):
        raise CompileError("'key value' expected", line_no)
    return parts[0], parts[1]

def parse_int(value: str, key: str, line_no: int) -> int:
    try:
        return int(value)
    except ValueError:
        raise CompileError(f"{key} debe ser un entero", line_no)