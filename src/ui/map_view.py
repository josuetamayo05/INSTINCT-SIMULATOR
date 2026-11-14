import tkinter as tk
from src.ui.colors import (TERRAIN_COLORS, OBJECT_COLORS, DEFAULT_TERRAIN,
                           DEFAULT_OBJECT, FactionColors)


class MapView(tk.Canvas):
    """Dibuja un World ajustando el tamaño de las celdas al espacio disponible. Solo lo lee: nunca lo modifica."""

    MIN_CELL = 8
    MAX_CELL = 64

    def __init__(self, master, cell_size: int = 32, **kwargs):
        super().__init__(master, highlightthickness=0, **kwargs)
        self.cell_size = 32
        self.factions = FactionColors()
        self.offset = (0, 0)        # margen para centrar el mapa
        self._world=None
        self.bind("<Configure>", lambda event: self._redraw())  # al cambiar de tamaño

    def draw(self, world) -> None:
        self._world=world
        self._redraw()

    def _layout(self, world):
        """Calcula el tamaño de celda y el margen para que el mapa quepa centrado."""
        w, h = self.winfo_width(), self.winfo_height()
        cs = min(w // world.width, h // world.height)
        cs = max(self.MIN_CELL, min(self.MAX_CELL, cs))
        ox = max(0, (w - cs * world.width) // 2)
        oy = max(0, (h - cs * world.height) // 2)
        return cs, ox, oy

    def _redraw(self) -> None:
        world = self._world
        if world is None:
            return
        cs, ox, oy = self._layout(world)
        self.cell_size, self.offset = cs, (ox, oy)
        pad = max(1, cs // 10)
        self.delete("all")
        for y, row in enumerate(world.grid):
            for x, cell in enumerate(row):
                x0, y0 = ox + x * cs, oy + y * cs
                x1, y1 = x0 + cs, y0 + cs
                self._draw_terrain(cell.terrain, x0, y0, x1, y1, cs)
                if cell.object:
                    self._draw_object(cell.object, x0 + pad, y0 + pad, x1 - pad, y1 - pad, cs)
                if cell.creature:
                    self._draw_creature(cell.creature, x0 + pad, y0 + pad, x1 - pad, y1 - pad, cs)

    def _draw_terrain(self, terrain, x0, y0, x1, y1, cs):
        known = terrain.name in TERRAIN_COLORS
        self.create_rectangle(x0, y0, x1, y1, outline="",
                              fill=TERRAIN_COLORS.get(terrain.name, DEFAULT_TERRAIN))
        if not known:   # terreno que no conocemos: mostramos su char para distinguirlo
            self.create_text((x0 + x1) // 2, (y0 + y1) // 2, text=terrain.char,
                             fill="#57534e", font=("Helvetica", max(6, cs // 2)))

    def _draw_object(self, obj, x0, y0, x1, y1, cs):
        known = obj.name in OBJECT_COLORS
        self.create_rectangle(x0, y0, x1, y1, outline="",
                              fill=OBJECT_COLORS.get(obj.name, DEFAULT_OBJECT))
        if not known:
            self.create_text((x0 + x1) // 2, (y0 + y1) // 2, text=obj.char,
                             fill="white", font=("Helvetica", max(6, cs // 2), "bold"))

    def _draw_creature(self, creature, x0, y0, x1, y1, cs):
        self.create_oval(x0, y0, x1, y1, fill=self.factions.get(creature.faction),
                         outline="white", width=max(1, cs // 16))
        if cs >= 14:   # con celdas muy pequeñas la letra no cabe
            self.create_text((x0 + x1) // 2, (y0 + y1) // 2, text=creature.species[0],
                             fill="white", font=("Helvetica", cs // 2, "bold"))

    def cell_at(self, px: int, py: int):
        """Convierte un clic en píxeles a (x, y) del mapa."""
        ox, oy = self.offset
        return (px - ox) // self.cell_size, (py - oy) // self.cell_size
