"""Catalogos base de lenguaje (percepciones, constantes, acciones y funciones)"""

# Constantes del mundo con valores enteros

WORLD_CONSTANTS = {
    "NONE": -1,
    "GROUND": 0,
    "OBJECT": 1,
    "ALLY": 2,
    "ENEMY": 3,
}

# Percepciones de solo lectura
READONLY_PERCEPTIONS= {
    # Propias
    "health", "age", "lifespan", "vision", "species", "faction",
    "x", "y", "terrain_here", "reserve_here",
    # Del mundo
    "width", "height", "tick",
    "total_creatures", "total_allies", "total_enemies",
    "random",
    # del entorno cercano
    "allies_near", "enemies_near", "objects_near",
    "enemy_dist", "enemy_dx", "enemy_dy",
    "ally_dist", "ally_dx", "ally_dy",
    "object_dist", "object_dx", "object_dy",
    "roars_near", "last_roar",
}

# Acciones base obligatorias y su cantidad exacta de argumentos
BUILTIN_ACTIONS = {
    "wait": 1,      # wait(n)
    "move": 3,      # move(dx, dy, speed)
    "attack": 3,    # attack(dx, dy, damage)
    "consume": 4,   # consume(dx, dy, damage, heal)
    "reproduce": 3, # reproduce(dx, dy, health)
    "roar": 1,      # roar(value)
    "say": 1,       # say(value)
}

BUILTIN_FUNCTIONS= {
    "see": 2,       # see(x, y)
    "name": 2,      # name(x, y)
}