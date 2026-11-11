"""AST Arbol de sintaxis abstracta, tomara la lista de tokens que genera el lexer 
y la convertira en una estructura de objetos que el programa puede entener"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from src.language.constants import BUILTIN_FUNCTIONS,WORLD_CONSTANTS
from src.language.errors import CompileError,InstinctRuntimeError
from src.language.context import ExecutionContext
from src.language.perceptions import get_perception
from src.language.constants import OPERATIONS


def is_truthy(value:Any)->bool:
        if isinstance(value,int):
            return value!=0
        if isinstance(value,str):
            return value!=""
        return bool(value)

# Base
class ASTNode:
    """Clase base para cualquier nodo del Arbol de Sintaxis Abstracta"""
    pass

#Expresiones, devuelven un valor al evaluarse
class Expression(ASTNode):
    """Clase Abstracta para todas las expresiones."""
    def check(self,line: int)-> None:
        """Validacion en compilacion. Por defecto no hay q revisar."""
        pass

    def evaluate(self, ctx:ExecutionContext):
        raise NotImplementedError

@dataclass
class LiteralInt(Expression):
    value: int

    def __repr__(self)-> str:
        return f"LiteralInt({self.value})"

    def evaluate(self, ctx):
        return self.value

@dataclass
class LiteralString(Expression):
    value:str

    def __repr__(self)->str:
        return f"LiteralString({repr(self.value)})"

    def evaluate(self, ctx):
        return self.value
    
@dataclass
class VariableRef(Expression):
    """Representa el uso de una variable, percepcion o constante ej (health,x,NONE)"""
    name:str

    def __repr__(self)->str:
        return f"VariableRef({self.name})"

    def evaluate(self, ctx):
        if self.name in WORLD_CONSTANTS:
            return WORLD_CONSTANTS[self.name]
        if self.name in ctx.creature.variables:
            return ctx.creature.variables[self.name]
        val=get_perception(self.name, ctx.creature, ctx.world, ctx.rng)
        if val is not None:
            return val
        raise InstinctRuntimeError(f"Variable '{self.name}' no definida", ctx.line)

@dataclass
class UnaryOp(Expression):
    """Operadores unarios: '-' (menos unario) y 'not' """
    op: str # '-' o 'not'
    expr:Expression

    def __repr__(self)->str:
        return f"UnaryOp({self.op}, {self.expr})"

    def check(self, line):
        self.expr.check(line)

    def evaluate(self, ctx):
        if self.op=="-":
            if not isinstance(self.expr,int):
                raise InstinctRuntimeError(f"Se esperaba un número para el operador '{self.op}'", ctx.line)
            return -self.expr
        if self.op=="not":
            return int(not is_truthy(self.expr.evaluate(ctx)))
        

@dataclass
class BinaryOp(Expression):
    """Operadores binarios: aritmeticos (+-*/%). comparaciones <>!= y logicos (and or)"""
    op:str
    left:Expression
    right:Expression

    def __repr__(self)->str:
        return f"BinaryOp({self.op}, {self.left}, {self.right})"

    def check(self, line):
        self.left.check(line)
        self.right.check(line)

    def evaluate(self, ctx):
        left=self.left.evaluate(ctx)
        right=self.right.evaluate(ctx)

        if self.op == "and": return int(is_truthy(left) and is_truthy(right))
        if self.op=="or": return int(is_truthy(left) or is_truthy(right))

        if type(left) is not type(right):
            raise InstinctRuntimeError(f"Operador '{self.op}': los dos lados deben tener el mismo tipo", ctx.line)

        if self.op == "==": return int(left==right)
        if self.op=="!=": return int(left!=right)

        if not isinstance(left, int):
            raise InstinctRuntimeError(f"Operador '{self.op}' requiere números", ctx.line)
        if self.op in ("/","%") and right == 0:
            raise InstinctRuntimeError("División por cero", ctx.line)
        if self.op=="/": return left//right
        if self.op=="%": return left % right
        return OPERATIONS[self.op](left, right)

@dataclass
class FunctionCall(Expression):
    """Representa una llamada a función, see(x,y),name(x,y)"""
    name: str
    args:List[Expression]

    def __repr__(self)->str:
        return f"FunctionCall({self.name}, {self.args})"

    def check(self, line):
        if self.name not in BUILTIN_FUNCTIONS:
            raise CompileError(f"Función desconocida: '{self.name}'", line)
        expected=BUILTIN_FUNCTIONS[self.name]
        if len(self.args)!=expected:
            raise CompileError(
            f"La función '{self.name}' espera {expected} argumento(s), "
            f"pero se le pasaron {len(self.args)}", line)
        for arg in self.args:
            arg.check(line)

    def evaluate(self, ctx):
        if self.name not in BUILTIN_FUNCTIONS:
            raise InstinctRuntimeError(f"Función desconocida: '{self.name}'", ctx.line)
        for arg in self.args:
            if not isinstance(arg,int):
                raise InstinctRuntimeError(f"Los argumentos deben ser enteros.")

        return FunctionCall(self.name,self.args)


# INSTRUCCIONES (Realizan una accion o controlan el flujo)
class Instruction(ASTNode):
    """Clase abstracta para todas las instruccuones de cuerpo"""
    line_number:int
    def check(self)-> None:
        pass

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
    target:int
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

    def check(self):
        self.condition.check(self.line_number)

@dataclass
class AssignmentInst(Instruction):
    """Asignacion de variable ej, ('home_x=x')"""
    variable_name:str
    value_expr: Expression
    line_number:int

    def __repr__(self)->str:
        return f"Action({self.variable_name} = {self.value_expr})"

    def check(self):
        self.value_expr.check(self.line_number)
@dataclass
class ActionInst(Instruction):
    """Llamada a accion ej ('move(1,0,2' o 'wait(1)'))"""
    action_name:str
    args: List[Expression]
    line_number:int

    def __repr__(self)->str:
        return f"Action({self.action_name}, {self.args})"

    def check(self):
        for a in self.args:
            a.check(self.line_number)


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

