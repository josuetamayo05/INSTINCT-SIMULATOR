"""Excepciones personalizadas para el lenguaje instinct"""

class InstinctError(Exception):
    pass

class LexerError(InstinctError):
    """Error en la tokenizacion (caracter desconocido, string sin cerrar, etc)."""
    def __init__(self, message:str, line: int, column: int):
        self.line=line
        self.column=column
        super().__init__(f"Error léxico en línea {line}, col {column}: {message}")

class CompileError(InstinctError):
    """Error durante el parsing o validacion semantica."""
    def __init__(self, message:str, line:int):
        self.line=line
        super().__init__(f"Error de compilación en línea {line}: {message}")

class InstinctRuntimeError(InstinctError):
    """Error durante la ejecucion de una criatuura"""
    def __init__(self, message:str, line:int):
        self.line=line
        super().__init__(f"Error en tiempo de ejecución en línea {line}: {message}")
