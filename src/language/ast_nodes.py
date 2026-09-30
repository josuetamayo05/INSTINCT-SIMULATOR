"""AST Arbol de sintaxis abstracta, tomara la lista de tokens que genera el lexer 
y la convertira en una estructura de objetos que el programa puede entener"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional

# Base
class ASTNode:
    """Clase base para cualquier nodo del Arbol de Sintaxis Abstracta"""
    pass

#Expresiones, devuelven un valor al evaluarse
class Expression(ASTNode):
    """Clase Abstracta para todas las expresiones."""
    pass

@dataclass
class LiteralInt(Expression):
    value: int

    def __repr__(self)-> str:
        return f"LiteralInt({self.value})"

@dataclass
class LiteralString(Expression):
    value:str

    def __repr__(self)->str:
        return f"LiteralString({repr(self.value)})"

@dataclass
class VariableRef(Expression):
    """Representa el uso de una variable, percepcion o constante ej (health,x,NONE)"""
    name:str

    def __repr__(self)->str:
        return f"VariableRef({self.name})"

@dataclass
class UnaryOp(Expression):
    """Operadores unarios: '-' (menos unario) y 'not' """
    op: str # '-' o 'not'
    expr:Expression

    def __repr__(self)->str:
        return f"UnaryOp({self.op}, {self.expr})"

@dataclass
class BinaryOp(Expression):
    """Operadores binarios: aritmeticos (+-*/%). comparaciones <>!= y logicos (and or)"""
    op:str
    left:Expression
    right:Expression

    def __repr__(self)->str:
        return f"BinaryOp({self.op}, {self.left}, {self.right})"

@dataclass
class FunctionCall(Expression):
    """Representa una llamada a función, see(x,y),name(x,y)"""
    name: str
    args:List[Expression]

    def __repr__(self)->str:
        return f"FunctionCall({self.name}, {self.args})"


# INSTRUCCIONES (Realizan una accion o controlan el flujo)

class Instruction(ASTNode):
    """Clase abstracta para todas las instruccuones de cuerpo"""
    line_number:int

@dataclass
class LabelInst(Instruction):
    """Representa una etiqueta (ej. 'start:', 'flee:'), no consume turno"""
    name:str
    line_number:int

    def __repr__(self)->str:
        return f"Label({self.name}:)"

@dataclass
class GotoInst(Instruction):
    """Salto incondicional (ej, 'goto start')"""
    target=int
    line_number:int

    def __repr__(self)->str:
        return f"Goto({self.target})"

@dataclass
class ConditionalGotoInst(Instruction):
    """Salto condicional (ej, 'if health < 20 goto flee')"""
    condition:Expression
    target:str
    line_number:int

    def __repr__(self)->str:
        return f"IfGoto({self.condition} -> {self.target})"

@dataclass
class AssignmentInst(Instruction):
    """Asignacion de variable ej, ('home_x=x')"""
    variable_name:str
    value_expr: Expression
    line_number:int

    def __repr__(self)->str:
        return f"Action({self.variable_name} = {self.value_expr})"

@dataclass
class ActionInst(Instruction):
    """Llamada a accion ej ('move(1,0,2' o 'wait(1)'))"""
    action_name:str
    args: List[Expression]
    line_number:int

    def __repr__(self)->str:
        return f"Action({self.action_name}, {self.args})"


#PROGRAMA COMPILADO COMPLETO    
class CompiledProgram:
    """Represente el resultado final de compilar un archivo .ins"""
    def __init__(self):
        self.creature_name:str=""
        self.faction:str=""
        self.health:int=0
        self.vision:int=0
        self.lifespan:int=0

        #Cuerpo
        self.instructions: List[Instruction]=[]

        # Mapa de etiquetas a indices de instruccion para saltos ultra rapidos ("start": 0, "flee": 14)
        self.labels: Dict[str,int]={}

    def __repr__(self)->str:
        return (
            f"CompiledProgram(\n"
            f"  Name: {self.creature_name}\n"
            f"  Faction: {self.faction}\n"
            f"  Health: {self.health}\n"
            f"  Vision: {self.vision}\n"
            f"  Lifespan: {self.lifespan}\n"
            f"  Instructions: {len(self.instructions)} lines\n"
            f"  Labels: {list(self.labels.keys())}\n"
            f")"
        )

