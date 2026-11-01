from typing import List, Dict, Set, Optional
from language.tokens import Token, TokenType
from language.ast_nodes import (
    CompiledProgram,
    Instruction,
    LabelInst,
    GotoInst,
    ConditionalGotoInst,
    AssignmentInst,
    ActionInst,
    Expression,
    LiteralInt,
    LiteralString,
    VariableRef,
    UnaryOp,
    BinaryOp,
    FunctionCall,
)
from language.errors import CompileError
from language.constants import (
    READONLY_PERCEPTIONS,
    WORLD_CONSTANTS,
    BUILTIN_ACTIONS,
    BUILTIN_FUNCTIONS,
)

REQUIRED_HEADER_KEYS = {"creature", "faction", "health", "vision", "lifespan"}


class Parser:
    """
    Toma una lista de tokens generada por el lexer y construye un CompileProgram.
    Implementa un analisis por descenso recursivo
    """

    def __init__(self, tokens:List[Token]):
        self.tokens=tokens
        self.current=0
        self.program=CompiledProgram()

    # Punto de entrada
    def parse(self) -> CompiledProgram:
        """Compila el archivo entero y devuelve un CompileProgram listo"""
        self._skip_newlines()
        self._parse_header()
        
        return self.program

    # Punto de entrada
    def _parse_header(self)->None:
        """
        Lee las 5 lineas de la cabecera, la 1ra debe ser 'creature Name'.
        Las otras 4 pueden estar en cualquier orden.
        Se detiende al encontrar la etiqueta 'start':
        """
        seen_keys=set()

        # Verificar que la Primera linea no vacia sea 'creature Name'
        if not self._check_identifier("creature"):
            raise CompileError(
                "La primera línea del archivo debe ser 'creature NombreEspecie'",
                self._peek().line
            )

        # leer lineas desde cabecera hasta encontrar 'start'
        while not self._is_at_end():
            if self._is_start_label(): 
                break  # Si detectamos el comienzo del cuerpo, terminamos la cabecera

            key_token=self._advance() # Consumimos el identificador ej, 'creature', 'health')

            if key_token.type!=TokenType.IDENTIFIER:
                raise CompileError(
                    f"Se esperaba una clave de cabecera (creature, faction, health, vision, lifespan), "
                    f"pero se encontró: '{key_token.value}'",
                    key_token.line
                )

            key=key_token.value

            if key not in REQUIRED_HEADER_KEYS:
                raise CompileError(
                    f"Clave de cabecera desconocida: '{key}'. "
                    f"Se esperaba una de: {REQUIRED_HEADER_KEYS}",
                    key_token.line
                )

            if key in seen_keys:
                raise CompileError(
                    f"La clave de cabecera '{key}' está declarada más de una vez",
                    key_token.line
                )
            seen_keys.add(key)
            self._parse_header_value(key, key_token.line)
            self._consume_newline(f"Se esperaba salto de línea tras la declaración de {key}")
            self._skip_newlines()

        # Al terminar, comprobar que se hayan leido las 5 claves
        missing=REQUIRED_HEADER_KEYS - seen_keys
        if missing:
            raise CompileError(
                f"Faltan claves de cabecera: {missing}",
                self._peek().line
            )

    def _parse_header_value(self,key:str,line:int)->None:
        """Lee el valor asociado a una clave cabecera y valida su tipo"""
        value_token=self._advance()

        # creature y faction esperan un nombre (identificador)
        if key in ("creature", "faction"):
            if value_token.type!=TokenType.IDENTIFIER:
                raise CompileError(
                    f"'{key}' requiere un nombre (identificador), no '{value_token.value}'",
                    line
                )
            if key=="creature":
                self.program.creature_name = value_token.value
            else:
                self.program.faction=value_token.value

        elif key in ("health","vision","lifespan"):
            if value_token.type != TokenType.NUMBER:
                raise CompileError(
                    f"'{key}' requiere un número entero, no '{value_token.value}'",
                    line
                )
            num=value_token.value

            if key=="health" and num <= 0:
                raise CompileError("'health' debe ser mayor que 0",line)
            if key=="vision" and num<1:
                raise CompileError("'vision' debe ser mayor o igual que 1",line)
            if key=="lifespan" and num<=0:
                raise CompileError("'lifespan' debe ser mayor que 0",line)

            if key=="health":
                self.program.health=num
            elif key == "vision":
                self.program.vision = num
            else:
                self.program.lifespan=num

    # 2 CUERPO DE INSTRUCCIONES
    def _parse_body(self)->None:
        """Parsea todas las lineas a partir de start: hasta el EOF"""
        if not self._is_start_label:
            raise CompileError("El cuerpo debe comenzar con la etiqueta 'start'",self._peek().line)

        while not self._is_at_end():
            self._skip_newlines()
            if self._is_at_end():
                break

            inst=self._parse_intruction_line()
            if inst is not None:
                self.program.instructions.append(inst)

            # Consumir el salto de linea al final de la instruccion
            if not self._is_at_end():
                self._consume_newline("Se esperaba salto de línea tras la instrucción")

    def _parse_instruction_line(self) -> Optional[Instruction]:
        token=self._peek()
        line=token.line

        # 1. Salto condicional: if <expr> goto <label>
        if self._match(TokenType.IF):
            condition=self.parse_expression()
            self._consume(TokenType.GOTO,"Se esperaba 'goto' tras la condición")
            label_token=self._consume(TokenType.IDENTIFIER,"Se esperaba una etiqueta tras 'goto'")
            return ConditionalGotoInst(condition,label_token.value,line)

        # 2. Salto incondicional: goto <label>
        if self._match(TokenType.GOTO):
            label_token=self._consume(TokenType.IDENTIFIER,"Se esperaba una etiqueta tras 'goto'")
            return GotoInst(label_token.value,line) 

        # Si empieza con IDENTIFIER, puede ser Etiqueta, Asignacion o Accion
        if self._check(TokenType.IDENTIFIER):
            name_token=self._advance()
            name=name_token.value

            # Caso 3: Etiqueta (name:)
            if self._match(TokenType.COLON):
                if name in self.program.labels:
                    raise CompileError(f"Etiqueta duplicada: '{name}'", line)
                 # la etiqueta apunta al indice de la instruccion actual de la lista
                self.program.labels[name]=len(self.program.instructions)
                return LabelInst(name, line)

            # Caso 4: Asignacion (name = <expr>)
            if self._match(TokenType.ASSIGN):
                if name in READONLY_PERCEPTIONS:
                    raise CompileError(f"No se puede asignar a la percepción de solo lectura: '{name}'", line)
                if name in WORLD_CONSTANTS:
                    raise CompileError(f"No se puede asignar un valor a la constante '{name}'",line)

                value_expr = self.parse_expression()
                return AssignmentInst(name,value_expr,line)

            # Caso 5: Accion (name(arg1,arg2,...))
            if self._match(TokenType.LPAREN):
                if name not in BUILTIN_ACTIONS:
                    raise CompileError(f"Accion desconocida: '{name}'",line)

                args=self._parse_argument_list()
                self._consume(TokenType.RPAREN,f"Se esperaba ')' tras los argumentos de '{name}'")

                expected_args=BUILTIN_ACTIONS[name]
                if len(args)!= expected_args:
                    raise CompileError(f"La acción '{name}' espera {expected_args} argumento(s), pero se le pasaron {len(args)}",line)

                return ActionInst(name,args,line)

            raise CompileError(f"Línea no válida o desconocida: '{token.value if token.value is not None else token.type.name}'",line)




    # Expresiones (tanda 2 Precedencia de menor a mayor)
    def parse_expression(self)-> Expression:
        """Punto de entrada para parsear cualquier expresion """
        return self._parse_or()

    def _parse_or(self)-> Expression:
        """Nivel 7: Operador logico 'or'"""
        expr=self._parse_and()

        while self._match(TokenType.OR):
            right= self._parse_and()
            expr= BinaryOp("or",expr,right)

        return expr

    def _parse_and(self)-> Expression:
        """Nivel 6: Operador logico 'and'"""
        expr=self._parse_comparison()

        while self._match(TokenType.AND):
            right= self._parse_comparison()
            expr= BinaryOp("and", expr,right)

        return expr

    def _parse_comparison(self)-> Expression:
        """Nivel 5: Comparaciones (<,<=,>,>=,==,!=)"""
        expr= self._parse_additive()
                    
        while self._peek().type in (
            TokenType.LESS,
            TokenType.LESS_EQUAL,
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.EQUAL_EQUAL,
            TokenType.BANG_EQUAL,
        ):
            op_token= self._advance()
            op_symbols= {
                TokenType.LESS: "<",
                TokenType.LESS_EQUAL: "<=",
                TokenType.GREATER: ">",
                TokenType.GREATER_EQUAL: ">=",
                TokenType.EQUAL_EQUAL: "==",
                TokenType.BANG_EQUAL: "!=",
            } 
            right= self._parse_additive()
            expr=BinaryOp(op_symbols[op_token.type],expr,right)

        return expr

    def _parse_additive(self)-> Expression:
        """Nivel 4: Suma (+) y Resta (-)"""
        expr=self._parse_multiplicative()

        while self._peek().type in (TokenType.PLUS,TokenType.MINUS):
            op_token=self._advance()
            op="+" if op_token.type == TokenType.PLUS else "-"
            right=self._parse_multiplicative()
            expr=BinaryOp(op,expr,right)

        return expr

    def _parse_multiplicative(self)-> Expression:
        """Nivel 3: Multiplicacion (*), Division entera (/), Modulo (%)"""
        expr=self._parse_unary()

        while self._peek().type in (TokenType.STAR, TokenType.SLASH,TokenType.PERCENT):
            op_token=self._advance()
            op_map={
                TokenType.STAR: "*",
                TokenType.SLASH: "/",
                TokenType.PERCENT: "%",
            }
            right=self._parse_unary()
            expr= BinaryOp(op_map[op_token.type],expr,right)

        return expr

    def _parse_unary(self)-> Expression:
        """Nivel 2: Menos unario (-) y Operador 'not'"""
        if self._peek().type in (TokenType.MINUS, TokenType.NOT):
            op_token=self._advance()
            op="-" if op_token.type == TokenType.MINUS else "not"
            operand = self._parse_unary() # Permite encadenar: --5 o not x
            return UnaryOp(op,operand)

        return self._parse_primary()

    def _parse_primary(self)-> Expression:
        """Nivel 1: Literales, variables, llamads a a funciones y parentesis"""
        token=self._peek()

        # 1. Literales Numericos
        if self._match(TokenType.NUMBER):
            return LiteralInt(token.value)

        # Literales texto
        if self._match(TokenType.STRING):
            return LiteralString(token.value)

        # Identificadores Variables,Percepciones,Constantes o Llamadas a Funciones
        if self._match(TokenType.IDENTIFIER):
            name=token.value
            # Si le sigue un parentesis '(', es una llamada a funcion ej see(x,y)
            if self._match(TokenType.LPAREN):
                args=self._parse_argument_list()
                self._consume(TokenType.RPAREN,f"Se esperaba ')' tras los argumentos de la funcion '{name}'")
                return FunctionCall(name,args)
            # si no, es una variable, percepcion o constante
            return VariableRef(name)
    
        # 4. Parentesis agrupadores: (expresion)
        if self._match(TokenType.LPAREN):
            expr = self.parse_expression()
            self._consume(TokenType.RPAREN, "Se esperaba ')' para cerrar la expresión")
            return expr

        raise CompileError(
            f"Expresión no válida o inesperada: '{token.value if token.value is not None else token.type.name}'",
            token.line
        )

    def _parse_argument_list(self)-> List[Expression]:
        """Lee una lista de expresiones separadas por comas """
        args:List[Expression] = []

        # Caso: Llamada sin argumentos ()
        if self._match(TokenType.RPAREN):
            return args 

        
        args.append(self.parse_expression())
        while self._match(TokenType.COMMA):
            args.append(self.parse_expression())

        return args

    # UTILIDADES DE NAVEGACION DE TOKENS

    def _peek(self,offset:int=0)->Token:
        """Mira el token en la posicion actual + offset sin consumirlo"""
        pos=self.current+offset
        if pos>=len(self.tokens):
            return self.tokens[-1] # EOF
        cur= self.tokens[pos]
        return cur
    
    def _advance(self)->Token:
        """Consume el token actual y avanza al siguiente"""
        token=self.tokens[self.current]
        if not self._is_at_end():
            self.current+=1
        return token

    def _is_at_end(self)->bool:
        return self._peek().type==TokenType.EOF

    def _check(self,token_type:TokenType)->bool:
        return self._peek().type == token_type

    def _check_identifier(self,name:str)->bool:
        """Comprueba si el token actual es un IDENTIFIER con ese nombre exacto."""
        return self._check(TokenType.IDENTIFIER) and self._peek().value == name

    def _is_start_label(self)->bool:
        """detecta el patron 'start' ':' para saber que empieza el cuerpo"""
        return (
            self._check_identifier("start") and self._peek(1).type==TokenType.COLON
        )

    def _consume(self,token_type:TokenType,error_msg:str)-> Token:
        """Consume el token actual si coincide con el tipo. Si no, lanza CompileError."""
        if self._check(token_type):
            return self._advance()
        raise CompileError(error_msg,self._peek().line)

    def _skip_newlines(self) -> None:
        """salta todos los salos de linea consecutivos (lineas en blanco)"""
        while self._check(TokenType.NEWLINE):
            self._advance()

    def _consume_newline(self,error_msg:str)->None:
        """Espera un salto de linea, si no lo encuentra, error"""
        if not self._check(TokenType.NEWLINE) and not self._is_at_end():
            raise CompileError(error_msg,self._peek().line)
        if self._check(TokenType.NEWLINE):
            self._advance()

    def _match(self,token_type:TokenType)->bool:
        """Si el token actual coincide con el tipo, lo consume y devuelve True; si no, False"""
        if self._check(token_type):
            self._advance()
            return True
        return False
