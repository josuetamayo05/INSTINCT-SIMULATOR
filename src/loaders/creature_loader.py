from src.language.lexer import Lexer
from src.language.parser import Parser
from src.language.ast_nodes import CompiledProgram

def load_creature(filepath:str) -> CompiledProgram:
    with open(filepath,"r",encoding="utf-8") as f:
        source=f.read()
    tokens=Lexer(source).tokenize()
    return Parser(tokens).parse()