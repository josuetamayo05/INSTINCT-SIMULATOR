from typing import Any, List
import random as _random_mod

from language.ast_nodes import (
    CompiledProgram, Expression, Instruction,
    LiteralInt, LiteralString, VariableRef,
    UnaryOp, BinaryOp, FunctionCall,
    LabelInst, GotoInst, ConditionalGotoInst,
    AssignmentInst, ActionInst,
)
from language.actions import ACTION_REGISTRY
from language.perceptions import get_perception
from language.constants import WORLD_CONSTANTS, READONLY_PERCEPTIONS
from language.errors import InstinctRuntimeError
from world.world import World
from world.creature import Creature

class Interpreter:
    def __init__(self,world:World,seed:int=42):
        self.world=world
        self.rng=_random_mod.Random(seed)

    def evaluate(self,expr:Expression,creature:Creature)->Any:
        if isinstance(expr,LiteralInt):
            return expr.value
        if isinstance(expr, LiteralString):
            return expr.value
        if isinstance(expr,VariableRef):
            name=expr.name
            if name in WORLD_CONSTANTS:
                return WORLD_CONSTANTS[name]
            if name in creature.variables:
                return creature.variables[name]
            val=get_perception(creature,name,self.world,self.rng)
            if val is not None:
                return val
            raise InstinctRuntimeError(f"Variable '{name}' no definida",0)
        if isinstance(expr,UnaryOp):
            val=self.evaluate(expr.expr,creature)
            if expr.op=="-":
                self._check_number(val,"-")
                return -val
            if expr.op=="not":
                return 0 if self._is_truthy(val) else 1
        if isinstance(expr,BinaryOp):
            return self._eval_binary(expr,creature)
        if isinstance(expr,FunctionCall):
            return self._eval_function_call(expr,creature)
        raise InstinctRuntimeError(f"Tipo de expresión desconocido: {type(expr)}",0)

    def _eval_binary(self,expr:BinaryOp,creature:Creature)->Any:
        left=self.evaluate(expr.left,creature)
        right=self.evaluate(expr.right,creature)

        if expr.op=="and":
            return 1 if self._is_truthy(left) and self._is_truthy(right) else 0
        if expr.op=="or":
            return 1 if self._is_truthy(left) or self._is_truthy(right) else 0

        if expr.op in ("==","!="):
            if expr.op=="==":
                return 1 if left==right else 0
            return 1 if left!=right else 0

        self._check_number(left,expr.op)
        self._check_number(right,expr.op)
        if expr.op==">":
            return 1 if left>right else 0
        if expr.op==">=":
            return 1 if left>=right else 0
        if expr.op=="<":
            return 1 if left<right else 0
        if expr.op=="<=":
            return 1 if left<=right else 0
        if expr.op=="+":
            return left+right
        if expr.op=="-":
            return left-right
        if expr.op=="*":
            return left*right
        if expr.op=="/":
            if right==0:
                raise InstinctRuntimeError("División por cero",0)
            return left//right
        if expr.op=="%":
            if right==0:
                raise InstinctRuntimeError("Módulo por cero",0)
            return left%right

        raise InstinctRuntimeError(f"Operador binario desconocido: {expr.op}",0)

    def _eval_function(self, expr: FunctionCall, creature: Creature)-> Any:
        args=[self.evaluate(arg, creature) for arg in expr.args]
        if expr.name=="see":
            return self._fn_name(creature,int(args[0]),int(args[1]))
        if expr.name=="name":
            return self._fn_name(creature,int(args[0]),int(args[1]))
        raise InstinctRuntimeError(f"Función desconocida: {expr.name}",0)

    def _fn_see(self,creature:Creature,x:int,y:int)->int:
        if self.world.chebyshev_distance(creature.x,creature.y,x,y)>creature.vision_range:
            return WORLD_CONSTANTS["NONE"]
        cell=self.world.get_cell(x,y)
        if cell is None:
            return WORLD_CONSTANTS["OBJECT"]
        if cell.creature: 
            if cell.creature.faction==creature.faction:
                return WORLD_CONSTANTS["ALLY"]
            return WORLD_CONSTANTS["ENEMY"]
        if cell.object:
            return WORLD_CONSTANTS["OBJECT"]
        return WORLD_CONSTANTS["GROUND"]

    def _fn_name(self,creature:Creature,x:int,y:int)->str:
        if self.world.chebyshev_distance(creature.x,creature.y,x,y)>creature.vision_range:
            return "UNKNOWN"
        cell=self.world.get_cell(x,y)
        if cell is None:
            return "UNKNOWN"
        if cell.creature: 
            return cell.creature.species
        if cell.object:
            return cell.object.name
        return cell.terrain.name

    def _is_truthy(self,value:Any)->bool:
        if isinstance(value,int):
            return value!=0
        if isinstance(value,str):
            return value!=""
        return bool(value)

    def _check_number(self,value:Any,op:str):
        if not isinstance(value,int):
            raise InstinctRuntimeError(f"Operador '{op}' requiere un número, pero se recibió: {value}",0)

    def run_turn(self, creature:Creature):
        if not creature.alive:
            return

        if creature.wait_remaining>0:
            creature.wait_remaining-=1
            return

        program: CompiledProgram = creature.program
        if not program or not program.instructions:
            return 

        creature.lines_executed= 0
        ip=creature.instruction_pointer

        while creature.lines_executed<100 and creature.alive:
            if ip>=len(program.instructions):
                ip=program.labels.get("start",0)

            inst=program.instructions[ip]
            creature.lines_executed+=1

            if isinstance(inst,LabelInst):
                ip+=1
                continue

            if isinstance(inst,GotoInst):
                ip=program.labels.get(inst.label,ip+1)
                continue

            if isinstance(inst, ConditionalGotoInst):
                condition=self.evaluate(inst.condition,creature)
                if self._is_truthy(condition):
                    ip=program.labels.get(inst.label,ip+1)
                else:
                    ip+=1
                continue

            if isinstance(inst,AssignmentInst):
                value=self.evaluate(inst.value,creature)
                creature.variables[inst.variable]=value
                ip+=1
                continue

            if isinstance(inst,ActionInst):
                action=ACTION_REGISTRY.get(inst.action_name)
                if not action:
                    raise InstinctRuntimeError(f"Acción desconocida: {inst.action_name}",0)
                args=[self.evaluate(arg,creature) for arg in inst.args]
                try:
                    action.execute(creature,self.world,args)
                except InstinctRuntimeError:
                    raise 
                except Exception as e:
                    raise InstinctRuntimeError(str(e),inst.line_number)
                ip+=1
                creature.instruction_pointer=ip
                return 

            ip+=1

        # Si llego a 100 lineas sin accion, equivale a wait(1)
        creature.instruction_pointer=ip