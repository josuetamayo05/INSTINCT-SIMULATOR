from language.lexer import Lexer
from language.tokens import TokenType
# Ejemplo de criatura uruk.ins del enunciado
sample_code = """# uruk.ins
creature Uruk
faction isengard
health 80
vision 6
lifespan 400

start:
    if health < 20 goto flee
    if enemy_dist == 1 goto bite
    move(random % 3 - 1, random % 3 - 1, 1)
    say("meat is back on the menu")
"""

def test_lexer():
    lexer = Lexer(sample_code)
    tokens = lexer.tokenize()
    print("--- TOKENS GENERADOS ---")
    for t in tokens:
        print(t)
    print("------------------------")
    print(f"Total de tokens: {len(tokens)}")

if __name__ == "__main__":
    test_lexer()