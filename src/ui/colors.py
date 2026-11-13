"""Colores de la interfaz. Lo que no esté aquí recibe un color por defecto,
así un terreno u objeto nuevo (water.te, tree.ob) se dibuja sin tocar código."""

TERRAIN_COLORS = {"Grass": "#8bc34a"}
OBJECT_COLORS = {"Rock": "#78716c"}
DEFAULT_TERRAIN = "#d6d3d1"
DEFAULT_OBJECT = "#44403c"

_PALETTE = ["#2563eb", "#dc2626", "#16a34a", "#9333ea", "#ea580c", "#0891b2"]


class FactionColors:
    """Asigna un color fijo a cada facción la primera vez que aparece."""

    def __init__(self):
        self._assigned = {}

    def get(self, faction: str) -> str:
        if faction not in self._assigned:
            self._assigned[faction] = _PALETTE[len(self._assigned) % len(_PALETTE)]
        return self._assigned[faction]