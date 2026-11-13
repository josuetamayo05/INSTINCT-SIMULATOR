import os
import unittest
from src.language.lexer import Lexer
from src.language.parser import Parser
from src.language.errors import CompileError
from src.loaders.creature_loader import load_creature

HEADER = "creature X\nfaction F\nhealth 10\nvision 1\nlifespan 10\nstart:\n"
CREATURES_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "creatures")


def compile_code(code):
    return Parser(Lexer(code).tokenize()).parse()


class TestEjemplosDelPDF(unittest.TestCase):
    """Las cuatro criaturas de data/creatures deben compilar."""

    def check_example(self, filename, name):
        program = load_creature(os.path.join(CREATURES_DIR, filename))
        self.assertEqual(program.creature_name, name)
        self.assertIn("start", program.labels)
        self.assertGreater(len(program.instructions), 0)

    def test_uruk(self):
        self.check_example("uruk.ins", "Uruk")

    def test_hobbit(self):
        self.check_example("hobbit.ins", "Hobbit")

    def test_ent(self):
        self.check_example("ent.ins", "Ent")

    def test_dwarf(self):
        self.check_example("dwarf.ins", "Dwarf")


class TestCabecera(unittest.TestCase):
    def test_cabecera_se_lee(self):
        program = compile_code(HEADER + "wait(1)")
        self.assertEqual(
            (program.creature_name, program.faction, program.health,
             program.vision, program.lifespan),
            ("X", "F", 10, 1, 10))

    def test_falta_start(self):
        with self.assertRaises(CompileError):
            compile_code("creature X\nfaction F\nhealth 10\nvision 1\nlifespan 10\nwait(1)")


class TestErroresDeCompilacion(unittest.TestCase):
    def assertCompileError(self, body):
        with self.assertRaises(CompileError):
            compile_code(HEADER + body)

    def test_asignar_a_percepcion(self):
        self.assertCompileError("health = 50")

    def test_asignar_a_constante(self):
        self.assertCompileError("GROUND = 5")

    def test_goto_inexistente(self):
        self.assertCompileError("goto fantasma")

    def test_if_goto_inexistente(self):
        self.assertCompileError("if health > 0 goto fantasma")

    def test_numero_de_argumentos(self):
        self.assertCompileError("move(1, 2)")

    def test_etiqueta_duplicada(self):
        self.assertCompileError("wait(1)\nstart:\nwait(1)")

    def test_error_indica_la_linea(self):
        with self.assertRaises(CompileError) as ctx:
            compile_code(HEADER + "wait(1)\ngoto fantasma")
        self.assertEqual(ctx.exception.line, 8)


class TestProgramasValidos(unittest.TestCase):
    def test_etiqueta_registrada(self):
        program = compile_code(HEADER + "wait(1)\nflee:\nwait(2)")
        self.assertIn("flee", program.labels)

    def test_goto_a_etiqueta_posterior(self):
        compile_code(HEADER + "goto later\nlater:\nwait(1)")

    def test_variables_propias(self):
        compile_code(HEADER + "home_x = x\nmove(home_x - x, 0, 1)")


if __name__ == "__main__":
    unittest.main()
