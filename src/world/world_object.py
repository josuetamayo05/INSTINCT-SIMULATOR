from dataclasses import dataclass

@dataclass
class WorldObject:
    name:str
    char:str
    resource_max:str
    reserve:int

    def __post_init__(self):
        self.reserve = self.resource_max

    def take_damage(self, amount:int)->int:
        actual=min(amount, self.reserve)
        self.reserve -= actual
        return actual

    def is_destroyed(self)->bool:
        return self.reserve <= 0