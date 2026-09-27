from typing import List, Any
from .tokens import Token, TokenType, KEYWORDS
from .errors import LexerError

class Lexer:
    """Convierte codigo fuente de instinct en una lista de tokens"""
    def __init__(self, source_code: str):
        self.source=source_code
        self.tokens: List[Token]=[]
        self.start=0
        self.current=0
        self.line=1
        self.column=1
        self.start_column=1

    def tokenize(self) -> List[Token]:
        """Recorre todo el texto y genera los tokens"""
        while not self._is_at_end():
            self.start = self.current
            self.start_column=self.column
            self._scan_token()

        # Emitir un ultimo NewLine si la utima linea tenia contenido
        if self.tokens and self.tokens[-1].type != TokenType.NEWLINE:
            self.tokens.append(Token(TokenType.NEWLINE, "\n", self.line,self.column))

        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens

    def _scan_token(self)->None:
        char=self._advance()

        # Epacios en blanco e indentacion se ignoran
        if char in (' ', '\t','\r'):
            return

        # saltos de linea
        if char =='\n':
            # evitar emitir multiples NewLine seguidos o al inicio
            if self.tokens and self.tokens[-1].type != TokenType.NEWLINE:
                self._add_token(TokenType.NEWLINE, "\n")
            self.line+=1
            self.column+=1
            return

        # Comentarios (#) hasta el fin de la linea
        if char =='#':
            while self._peek() != '\n' and not self._is_at_end():
                self._advance()
            return
        
        # delimitadores y operadores simples
        if char == '(':
            self._add_token(TokenType.LPAREN)
        elif char == ')':
            self._add_token(TokenType.RPAREN)
        elif char ==',':
            self._add_token(TokenType.COMMA)
        elif char == ':':
            self._add_token(TokenType.COLON)
        elif char =='+':
            self._add_token(TokenType.PLUS)
        elif char =='-':
            self._add_token(TokenType.MINUS)
        elif char == '*':
            self._add_token(TokenType.STAR)
        elif char =='/':    
            self._add_token(TokenType.SLASH)
        elif char =='%':
            self._add_token(TokenType.PERCENT)
        
        # Operadores dobles o simples (=,==,<,<=,>,>=,!=)
        elif char=='=':
            if self._match('='):
                self._add_token(TokenType.EQUAL_EQUAL)
            else:
                self.add_token(TokenType.ASSIGN)
        elif char =='!':
            if self._match('='):
                self._add_token(TokenType.BANG_EQUAL)
            else:
                raise LexerError("Se esperaba '=' después de '!'",self.line,self.start_column)
        elif char =='<':
            if self._match('='):
                self._add_token(TokenType.LESS_EQUAL)
            else:
                self._add_token(TokenType.LESS)
        elif char == '>':
            if self._match('='):
                self._add_token(TokenType.GREATER_EQUAL)
            else:
                self._add_token(TokenType.GREATER)

        # Literales de texto ("...")
        elif char == '"':
            self._string()

        # Literales numericos
        elif char.isdigit():
            self._number()

        elif char.isalpha() or char =='_':
            self._identifier()

        else:
            raise LexerError(f"Carácter inesperado: '{char}'",self.line,self.start_column)

    # metodos auxiliares

    def _advance(self)->str:
        char=self.source[self.current]
        self.current+=1
        self.column+=1
        return char

    def _match(self,expected:str)->bool:
        if self._is_at_end() or self.source[self.current] != expected:
            return False
        self.current+=1
        self.column+=1
        return True

    def _peek(self)->str:
        if self._is_at_end():
            return '\0'
        return self.source[self.current]

    def _is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def _add_token(self,token_type: TokenType, value:Any=None)->None:
        self.tokens.append(Token(token_type,value,self.line,self.start_column))

    # literales complejos
    def _string(self) -> None:
        value_chars=[]
        while self._peek() != '*' and not self._is_at_end():
            if self._peek() == '\n':
                raise LexerError("Cadena de texto sin cerrar antes del fin de linea", self.line, self.start_column)
            value_chars.append(self._advance())

        if self._is_at_end():
            raise LexerError("Cadena de texto sin cerrar al final del archivo", self.line, self.start_column)

        self._advance() # Consumir la commila de cierre
        self._add_token(TokenType.STRING, "".join(value_chars))

    def _number(self)-> None:
        while self._peek().isdigit():
            self._advance()
        num_str=self.source[self.start:self.current]
        self._add_token(TokenType.NUMBER, int(num_str))

    def _identifier(self)-> None:
        while self._peek().isalnum() or self._peek() == '_':
            self._advance()

        text = self.source[self.start:self.current]
        # Comprobar si es palabra clave (if, goto, and, or, not ) o identificador libre
        token_type=KEYWORDS.get(text, TokenType.IDENTIFIER)
        self._add_token(token_type,text if token_type == TokenType.IDENTIFIER else None)
