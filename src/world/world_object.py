from dataclasses import dataclass

@dataclass
class WorldObject:
    name:str
    char:str
    resource_max: int 
    reserve:int = 0

    def __post_init__(self):
        self.reserve = self.resource_max

    def take_damage(self, amount:int)->int:
        actual=min(amount, self.reserve)
        self.reserve -= actual
        return actual

    def is_destroyed(self)->bool:
        return self.reserve <= 0

    def copy(self):
        return WorldObject(self.name, self.char, self.resource_max)