from typing import List, Optional,Tuple
from src.world.creature import Creature
from src.world.cell import Cell
from src.world.terrain import Terrain
from src.world.world_object import WorldObject
from dataclasses import dataclass

@dataclass
class EventLog:
    tick: int
    message: str

class World:
    def __init__(self,width:int,height:int,default_terrain:Terrain):
        self.width=width
        self.height=height
        self.grid:List[List[Cell]]=[]
        self.creatures:List[Creature]=[]
        self.tick_count=0
        self.roar_buffer:List[Tuple[int,int,str]]= []  # (x, y, message) del tick anterior
        self.events: List[EventLog]=[]

        for i in range(height):
            row=[]
            for j in range(width):
                row.append(Cell(default_terrain.copy()))
            self.grid.append(row)

    def add_event(self, message:str)->None:
        """Registrar un nuevo evento con el numero del tick"""
        log= EventLog(self.tick_count, message)
        self.events.append(log)

    def in_bounds(self,x:int,y:int)->bool:
        return 0<=x<self.width and 0<=y<self.height

    def get_cell(self,x:int,y:int)->Optional[Cell]:
        if self.in_bounds(x,y):
            return self.grid[y][x]
        return None

    def place_creature(self,creature:Creature,x:int,y:int)->bool:
        cell=self.get_cell(x,y)
        if cell and cell.is_walkable():
            cell.creature=creature
            creature.x=x
            creature.y=y
            self.creatures.append(creature)
            return True
        return False

    def remove_creature(self,creature:Creature):
        cell=self.get_cell(creature.x,creature.y)
        creature.alive=False
        if cell and cell.creature is creature:
            cell.creature=None
            self.creatures.remove(creature)

    def move_creature(self,creature:Creature,new_x:int,new_y:int,speed: int)->None:
        for _ in range(speed):
            nx, ny= creature.x+new_x, creature.y+new_y
            cell=self.get_cell(nx, ny)
            if cell is None or not cell.is_walkable():
                break
            self.get_cell(creature.x,creature.y).creature=None
            creature.x=nx
            creature.y=ny
            cell.creature=creature

    def get_target_cell(self, creature:Creature, dx:int,dy:int)->Optional[Cell]:
        if dx==0 and dy==0:
            return self.get_cell(creature.x,creature.y)
        return self.get_cell(creature.x+dx, creature.y+dy)

    def chebyshev_distance(self, x1:int, y1:int, x2:int, y2:int )-> int:
        return max(abs(x2-x1),abs(y2-y1))

    def alive_creatures(self)->List[Creature]:
        return [c for c in self.creatures if c.alive]

    def end_of_tick(self):
        # 1 y 2 Vida, edad muertes
        for c in self.alive_creatures():
            c.end_of_tick()
        for c in list(self.creatures):
            if c.is_dead() and c.alive:
                self.remove_creature(c)

        # 3: Regenerar terrenos
        for row in self.grid:
            for cell in row:
                cell.terrain.regenerate()

        # 4: Objetos destruidos
        for row in self.grid:
            for cell in row:
                if cell.object and cell.object.is_destroyed():
                    cell.object=None

        self.tick_count+=1
