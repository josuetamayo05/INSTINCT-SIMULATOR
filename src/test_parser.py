from language.lexer import Lexer
from language.parser import Parser


def parse_single_expr(expr_str: str):
    tokens = Lexer(expr_str).tokenize()
    parser = Parser(tokens)
    return parser.parse_expression()


def test_expressions():
    print("=== PRUEBAS DE EXPRESIONES ===")

    # 1. Precedencia aritmética: 1 + 2 * 3  ->  debe ser 1 + (2 * 3)
    expr1 = parse_single_expr("1 + 2 * 3")
    print(f"1 + 2 * 3  -->  {expr1}")

    # 2. Expresión del Uruk: random % 3 - 1
    expr2 = parse_single_expr("random % 3 - 1")
    print(f"random % 3 - 1  -->  {expr2}")

    # 3. Expresión del Ent: (home_x > x) - (home_x < x)
    expr3 = parse_single_expr("(home_x > x) - (home_x < x)")
    print(f"(home_x > x) - (home_x < x)  -->  {expr3}")

    # # 4. Condición con lógica y comparación: health < 20 and enemy_dist < 3
    expr4 = parse_single_expr("health < 20 and enemy_dist < 3")
    print(f"health < 20 and enemy_dist < 3  -->  {expr4}")

    # 5. Funciones con argumentos complejos: see(x, y + 1) != GROUND
    expr5 = parse_single_expr("see(x, y + 1) != GROUND")
    print(f"see(x, y + 1) != GROUND  -->  {expr5}")

    # 6. Función name con strings: name(x + object_dx, y + object_dy) != \"Rock\"
    expr6 = parse_single_expr('name(x + object_dx, y + object_dy) != "Rock"')
    print(f'name(...) != "Rock"  -->  {expr6}')

    # 7. Operadores unarios combinados: not alive or -enemy_dx
    expr7 = parse_single_expr("not alive or -enemy_dx")
    print(f"not alive or -enemy_dx  -->  {expr7}")

    print("\n✅ ¡Todas las expresiones se parsearon con éxito!")


if __name__ == "__main__":
    test_expressions()