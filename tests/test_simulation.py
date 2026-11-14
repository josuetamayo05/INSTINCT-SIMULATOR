import random
import unittest
from src.world.world import World
from src.world.terrain import Terrain
from src.world.world_object import WorldObject
from src.world.creature import Creature
from src.language.lexer import Lexer
from src.language.parser import Parser
from src.language.actions import ACTION_REGISTRY
from src.language.perceptions import PERCEPTIONS
from src.language.interpreter import Interpreter
from src.simulation.simulation import Simulation
from src.language.errors import InstinctRuntimeError


def make_world(width=10, height=10):
    return World(width, height, Terrain("Grass", ".", 100, 2))

def make_creature(world, x, y, faction="f1", health=50, vision=3, program=None):
    c = Creature("A", faction, health, vision, 100, program=program)
    world.place_creature(c, x, y)
    return c

def compile_body(body):
    code = "creature A\nfaction f1\nhealth 50\nvision 3\nlifespan 100\nstart:\n" + body
    return Parser(Lexer(code).tokenize()).parse()

def perceive(name, creature, world):
    return PERCEPTIONS[name].read(creature, world, random.Random(0))

def act(name, creature, world, *args):
    ACTION_REGISTRY[name].execute(creature, world, list(args))


class TestAcciones(unittest.TestCase):
    def test_attack_0_0_golpea_el_terreno_propio(self):
        world = make_world()
        c = make_creature(world, 5, 5)
        act("attack", c, world, 0, 0, 10)
        self.assertEqual(world.get_cell(5, 5).terrain.reserve, 90)
        self.assertEqual(c.health, 50)

    def test_consume_0_0_cura_y_quita_reserva(self):
        world = make_world()
        c = make_creature(world, 5, 5)
        act("consume", c, world, 0, 0, 10, 7)
        self.assertEqual(world.get_cell(5, 5).terrain.reserve, 90)
        self.assertEqual(c.health, 57)

    def test_attack_a_criatura_adyacente(self):
        world = make_world()
        a = make_creature(world, 5, 5)
        b = make_creature(world, 6, 5, faction="f2")
        act("attack", a, world, 1, 0, 20)
        self.assertEqual(b.health, 30)

    def test_attack_mortal_deja_la_casilla_libre(self):
        world = make_world()
        a = make_creature(world, 5, 5)
        b = make_creature(world, 6, 5, faction="f2", health=10)
        act("attack", a, world, 1, 0, 10)
        self.assertFalse(b.alive)
        self.assertIsNone(world.get_cell(6, 5).creature)

    def test_attack_a_objeto_quita_reserva(self):
        world = make_world()
        a = make_creature(world, 5, 5)
        world.get_cell(6, 5).object = WorldObject("Rock", "#", 100)
        act("attack", a, world, 1, 0, 30)
        self.assertEqual(world.get_cell(6, 5).object.reserve, 70)

    def test_attack_fuera_del_mapa_no_hace_nada(self):
        world = make_world()
        a = make_creature(world, 0, 0)
        act("attack", a, world, -1, -1, 10)
        self.assertEqual(a.health, 50)

    def test_move_se_detiene_ante_un_objeto(self):
        world = make_world()
        a = make_creature(world, 0, 0)
        world.get_cell(3, 0).object = WorldObject("Rock", "#", 100)
        act("move", a, world, 1, 0, 5)
        self.assertEqual((a.x, a.y), (2, 0))

    def test_reproduce_crea_cria_y_cuesta_vida(self):
        world = make_world()
        a = make_creature(world, 5, 5)
        act("reproduce", a, world, 0, 1, 20)
        baby = world.get_cell(5, 6).creature
        self.assertIsNotNone(baby)
        self.assertEqual(baby.faction, a.faction)
        self.assertEqual(a.health, 30)

    def test_say_no_consume_turno_y_el_resto_si(self):
        self.assertFalse(ACTION_REGISTRY["say"].consumes_turn)
        for name in ("wait", "move", "attack", "consume", "reproduce", "roar"):
            self.assertTrue(ACTION_REGISTRY[name].consumes_turn, name)

    def test_texto_como_argumento_numerico_falla(self):
        world = make_world()
        a = make_creature(world, 5, 5)
        with self.assertRaises(Exception):
            act("wait", a, world, "hola")


class TestPercepciones(unittest.TestCase):
    def test_total_allies_cuenta_todo_el_mapa(self):
        world = make_world(20, 20)
        me = make_creature(world, 0, 0, vision=2)
        make_creature(world, 19, 19)               # aliado lejos
        make_creature(world, 1, 1)                 # aliado cerca
        make_creature(world, 10, 10, faction="f2") # enemigo
        self.assertEqual(perceive("total_allies", me, world), 2)
        self.assertEqual(perceive("total_enemies", me, world), 1)
        self.assertEqual(perceive("total_creatures", me, world), 3)

    def test_allies_near_solo_cuenta_la_vision(self):
        world = make_world(20, 20)
        me = make_creature(world, 0, 0, vision=2)
        make_creature(world, 19, 19)
        make_creature(world, 1, 1)
        self.assertEqual(perceive("allies_near", me, world), 1)

    def test_enemigo_mas_cercano(self):
        world = make_world()
        me = make_creature(world, 5, 5)
        make_creature(world, 3, 7, faction="f2")
        self.assertEqual(perceive("enemy_dist", me, world), 2)
        self.assertEqual(perceive("enemy_dx", me, world), -1)
        self.assertEqual(perceive("enemy_dy", me, world), 1)

    def test_sin_enemigo_visible(self):
        world = make_world(20, 20)
        me = make_creature(world, 0, 0, vision=2)
        make_creature(world, 19, 19, faction="f2")
        self.assertEqual(perceive("enemy_dist", me, world), -1)
        self.assertEqual(perceive("enemy_dx", me, world), 0)

    def test_roars_near_cuenta_todos(self):
        world = make_world()
        me = make_creature(world, 5, 5)
        world.roar_buffer = [(4, 4, "uno"), (6, 6, "dos"), (0, 9, "lejos")]
        self.assertEqual(perceive("roars_near", me, world), 2)
        self.assertEqual(perceive("last_roar", me, world), "dos")

    def test_sin_rugidos(self):
        world = make_world()
        me = make_creature(world, 5, 5)
        self.assertEqual(perceive("roars_near", me, world), 0)
        self.assertEqual(perceive("last_roar", me, world), "")

    def test_terreno_bajo_la_criatura(self):
        world = make_world()
        me = make_creature(world, 5, 5)
        self.assertEqual(perceive("terrain_here", me, world), "Grass")
        self.assertEqual(perceive("reserve_here", me, world), 100)


class TestInterprete(unittest.TestCase):
    def run_one_turn(self, body):
        world = make_world()
        c = make_creature(world, 5, 5, program=compile_body(body))
        Interpreter(world, seed=1).run_turn(c)
        return c

    def test_random_cambia_en_cada_lectura(self):
        # PDF 2.6: "distinto cada vez que se lee"
        c = self.run_one_turn("a = random\nb = random\nc = random\nwait(1)")
        values = {c.variables["a"], c.variables["b"], c.variables["c"]}
        self.assertGreater(len(values), 1)

    def test_resto_de_percepciones_fijas_en_el_turno(self):
        # health se lee al inicio del turno: consume no la cambia hasta el siguiente
        c = self.run_one_turn('h = health\nsay("x")\nconsume(0, 0, 1, 10)')
        self.assertEqual(c.variables["h"], 50)

    def test_dx_fuera_de_rango_es_error_con_su_linea(self):
        # PDF 2.8: dx o dy fuera de {-1, 0, 1} es error de ejecucion
        for action in ("attack(2, 0, 5)", "consume(0, 5, 1, 1)",
                       "reproduce(3, 0, 1)", "move(2, 0, 1)"):
            world = make_world()
            c = make_creature(world, 5, 5, program=compile_body("wait(1)\n" + action))
            interp = Interpreter(world, seed=1)
            interp.run_turn(c)
            with self.assertRaises(InstinctRuntimeError) as ctx:
                interp.run_turn(c)
            self.assertEqual(ctx.exception.line, 8, action)

    def test_el_turno_acaba_en_la_primera_accion(self):
        c = self.run_one_turn("move(1, 0, 1)\nmove(1, 0, 1)")
        self.assertEqual(c.x, 6)

    def test_say_no_acaba_el_turno(self):
        c = self.run_one_turn('say("hola")\nmove(1, 0, 1)')
        self.assertEqual(c.x, 6)

    def test_sigue_donde_se_quedo(self):
        world = make_world()
        c = make_creature(world, 0, 5, program=compile_body("move(1, 0, 1)\nmove(0, 1, 1)"))
        interp = Interpreter(world, seed=1)
        interp.run_turn(c)
        interp.run_turn(c)
        self.assertEqual((c.x, c.y), (1, 6))


class TestSimulacion(unittest.TestCase):
    """Simulation trabaja sobre una copia del mundo: se comprueba sim.world."""

    def start(self, world, seed=1):
        return Simulation(world, seed=seed)

    def test_error_de_ejecucion_mata_y_queda_en_el_log(self):
        world = make_world()
        make_creature(world, 5, 5, program=compile_body('wait("hola")'))
        sim = self.start(world)
        sim.tick()
        self.assertTrue(sim.is_over)
        self.assertTrue(sim.events_since(0))

    def test_fin_de_tick_resta_vida_y_suma_edad(self):
        world = make_world()
        make_creature(world, 5, 5, program=compile_body("wait(1)"))
        sim = self.start(world)
        sim.tick()
        c = sim.world.creatures[0]
        self.assertEqual((c.health, c.age), (49, 1))
        self.assertEqual(sim.tick_count, 1)

    def test_rugido_se_oye_en_el_tick_siguiente(self):
        world = make_world()
        make_creature(world, 5, 5, program=compile_body('roar("hey")'))
        make_creature(world, 6, 6, program=compile_body("wait(1)"))
        sim = self.start(world)
        sim.tick()
        listener = sim.world.get_cell(6, 6).creature
        self.assertEqual(perceive("last_roar", listener, sim.world), "hey")

    def test_objeto_destruido_desaparece(self):
        world = make_world()
        make_creature(world, 5, 5, program=compile_body("attack(1, 0, 100)"))
        world.get_cell(6, 5).object = WorldObject("Rock", "#", 100)
        sim = self.start(world)
        sim.tick()
        self.assertIsNone(sim.world.get_cell(6, 5).object)

    def test_muchos_ticks_sin_errores(self):
        world = make_world(20, 20)
        program = compile_body("move(random % 3 - 1, random % 3 - 1, 1)")
        for i in range(5):
            make_creature(world, i, 0, program=program)
        sim = self.start(world, seed=42)
        for _ in range(50):
            sim.tick()
        self.assertEqual(sim.tick_count, 50)

    def test_reset_vuelve_al_estado_inicial(self):
        world = make_world()
        make_creature(world, 5, 5, program=compile_body("move(1, 0, 1)"))
        sim = self.start(world)
        sim.tick(); sim.tick()
        sim.reset()
        self.assertEqual(sim.tick_count, 0)
        self.assertEqual(sim.world.creatures[0].x, 5)
        self.assertEqual(world.creatures[0].x, 5)   # el de preparacion no se toco

    def test_misma_semilla_misma_partida(self):
        world = make_world(20, 20)
        program = compile_body("move(random % 3 - 1, random % 3 - 1, 1)")
        make_creature(world, 10, 10, program=program)
        sim = self.start(world, seed=7)
        for _ in range(20):
            sim.tick()
        first = (sim.world.creatures[0].x, sim.world.creatures[0].y)
        sim.reset()
        for _ in range(20):
            sim.tick()
        self.assertEqual((sim.world.creatures[0].x, sim.world.creatures[0].y), first)

    def test_simulacion_no_toca_el_mundo_de_preparacion(self):
        world = make_world()
        make_creature(world, 5, 5, program=compile_body("move(1, 0, 1)"))
        sim = self.start(world)
        sim.tick()
        self.assertEqual(world.creatures[0].x, 5)
        self.assertEqual(world.tick_count, 0)


if __name__ == "__main__":
    unittest.main()
