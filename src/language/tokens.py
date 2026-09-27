from enum import Enum, auto
from dataclasses import dataclass
from typing import Any

class TokenType(Enum):
    # Palabras reservadas base
    IF = auto()
    GOTO = auto()
    AND =auto()
    OR=auto()
    NOT=auto()

    # Literales e identificadores 
    IDENTIFIER=auto() # Nombres de variables, acciones, percepciones, cabeceras
    NUMBER=auto()
    STRING=auto()

    # Operadores aritmeticos
    PLUS=auto() # +
    MINUS=auto() # -
    STAR=auto() # *
    SLASH=auto() # / (division entera)
    PERCENT=auto() # % (modulo)

    # Operadores de comparacion
    LESS=auto() # <
    LESS_EQUAL=auto() # <=
    GREATER=auto() # >
    GREATER_EQUAL=auto() # >=
    EQUAL_EQUAL=auto() # ==
    BANG_EQUAL=auto() # !=

    # Asignacion y delimitadores
    ASSIGN=auto() # =
    COLON=auto() # : (PARA ETIQUETAS) 
    COMMA=auto() # ,
    LPAREN=auto() # (
    RPAREN=auto() # )

    # Control de flujo de lineas
    NEWLINE=auto() # SALTO DE LINEA
    EOF=auto() #FIN DE ARCHIVO 

# Mapeo de palabras clave reservadas
KEYWORDS = {
    "if": TokenType.IF,
    "goto": TokenType.GOTO,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
}

@dataclass
class Token:
    type: TokenType
    value:Any
    line:int
    column:int

    def __repr__(self):
        if self.value is not None:
            return f"Token({self.type.name}, {repr(self.value)}, L{self.line}:C{self.column})"
        return f"Token({self.type.name}, L{self.line}:C{self.column})"