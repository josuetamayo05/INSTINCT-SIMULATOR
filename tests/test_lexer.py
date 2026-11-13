import unittest
from src.language.lexer import Lexer
from src.language.tokens import TokenType
from src.language.errors import LexerError


def types(code):
    return [t.type for t in Lexer(code).tokenize()]


class TestLexer(unittest.TestCase):
    def test_asignacion_simple(self):
        self.assertEqual(
            types("a = 5"),
            [TokenType.IDENTIFIER, TokenType.ASSIGN, TokenType.NUMBER,
             TokenType.NEWLINE, TokenType.EOF])

    def test_palabras_clave(self):
        self.assertEqual(
            types("if not a and b or c goto x")[:8],
            [TokenType.IF, TokenType.NOT, TokenType.IDENTIFIER, TokenType.AND,
             TokenType.IDENTIFIER, TokenType.OR, TokenType.IDENTIFIER, TokenType.GOTO])

    def test_operadores_dobles(self):
        self.assertEqual(
            types("<= >= == != < >")[:6],
            [TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL, TokenType.EQUAL_EQUAL,
             TokenType.BANG_EQUAL, TokenType.LESS, TokenType.GREATER])

    def test_valores_de_numero_y_texto(self):
        tokens = Lexer('say("hola mundo")\nwait(42)').tokenize()
        self.assertEqual(tokens[2].type, TokenType.STRING)
        self.assertEqual(tokens[2].value, "hola mundo")
        number = next(t for t in tokens if t.type == TokenType.NUMBER)
        self.assertEqual(number.value, 42)

    def test_comentarios_se_ignoran(self):
        self.assertEqual(types("# solo un comentario"), [TokenType.EOF])
        self.assertEqual(types("wait(1) # al final"), types("wait(1)"))

    def test_lineas_vacias_no_repiten_newline(self):
        self.assertEqual(types("a = 1\n\n\nb = 2").count(TokenType.NEWLINE), 2)

    def test_numero_de_linea(self):
        tokens = Lexer("a = 1\nb = 2").tokenize()
        b = next(t for t in tokens if t.value == "b")
        self.assertEqual((b.line, b.column), (2, 1))

    def test_texto_sin_cerrar(self):
        with self.assertRaises(LexerError):
            Lexer('say("hola)').tokenize()

    def test_caracter_desconocido(self):
        with self.assertRaises(LexerError) as ctx:
            Lexer("a = 5 $").tokenize()
        self.assertEqual(ctx.exception.line, 1)

    def test_comillas_curvas(self):
        with self.assertRaises(LexerError):
            Lexer("say(“hola”)").tokenize()

    def test_exclamacion_sola(self):
        with self.assertRaises(LexerError):
            Lexer("if a ! b goto x").tokenize()


if __name__ == "__main__":
    unittest.main()
