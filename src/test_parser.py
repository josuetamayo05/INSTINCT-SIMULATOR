from language.lexer import Lexer
from language.parser import Parser

sample_code="""# uruk.ins
creature Uruk
faction isengard
health 80
vision 6
lifespan 400

start:
"""

def test_header_parsing():
    print("=== Tokenizando ===")
    lexer = Lexer(sample_code)
    tokens = lexer.tokenize()
    print(f"Tokens generados: {len(tokens)}\n")

    print("=== Parseando ===")
    parser = Parser(tokens)
    program = parser.parse()

    print("=== Resultado ===")
    print(program)

def test_header_missing_key():
    """Verifica que el parser detecte una cabecera incompleta."""
    bad_code = """creature Uruk
faction isengard
health 80
start:
"""
    print("\n=== Prueba: cabecera incompleta ===")
    try:
        tokens = Lexer(bad_code).tokenize()
        Parser(tokens).parse()
        print("ERROR: Debía haber lanzado excepción")
    except Exception as e:
        print(f"OK - Se detectó el error: {e}")

def test_header_wrong_first_line():
    """Verifica que el parser detecte un archivo que no empiece por 'creature'."""
    bad_code = """faction isengard
creature Uruk
health 80
vision 6
lifespan 400
start:
"""
    print("\n=== Prueba: primera línea incorrecta ===")
    try:
        tokens = Lexer(bad_code).tokenize()
        Parser(tokens).parse()
        print("ERROR: Debía haber lanzado excepción")
    except Exception as e:
        print(f"OK - Se detectó el error: {e}")

if __name__ == "__main__":
    test_header_parsing()
    test_header_missing_key()
    test_header_wrong_first_line()


