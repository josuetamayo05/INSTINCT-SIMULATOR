import tkinter as tk
from src.ui.colors import (TERRAIN_COLORS, OBJECT_COLORS, DEFAULT_TERRAIN,
                           DEFAULT_OBJECT, FactionColors)


class MapView(tk.Canvas):
    """Dibuja un World. Solo lo lee: nunca lo modifica."""

    def __init__(self, master, cell_size: int = 32, **kwargs):
        super().__init__(master, highlightthickness=0, **kwargs)
        self.cell_size = cell_size
        self.factions = FactionColors()

    def draw(self, world) -> None:
        cs = self.cell_size
        self.delete("all")
        self.config(width=world.width * cs, height=world.height * cs)
        for y, row in enumerate(world.grid):
            for x, cell in enumerate(row):
                x0, y0 = x * cs, y * cs
                x1, y1 = x0 + cs, y0 + cs
                terrain = TERRAIN_COLORS.get(cell.terrain.name, DEFAULT_TERRAIN)
                self.create_rectangle(x0, y0, x1, y1, fill=terrain, outline="")
                if cell.object:
                    color = OBJECT_COLORS.get(cell.object.name, DEFAULT_OBJECT)
                    self.create_rectangle(x0 + 3, y0 + 3, x1 - 3, y1 - 3,
                                          fill=color, outline="")
                if cell.creature:
                    c = cell.creature
                    self.create_oval(x0 + 3, y0 + 3, x1 - 3, y1 - 3,
                                     fill=self.factions.get(c.faction),
                                     outline="white", width=2)
                    self.create_text((x0 + x1) // 2, (y0 + y1) // 2,
                                     text=c.species[0], fill="white",
                                     font=("Helvetica", cs // 2, "bold"))

    def cell_at(self, px: int, py: int):
        """Convierte un clic en píxeles a (x, y) del mapa."""
        return px // self.cell_size, py // self.cell_size
