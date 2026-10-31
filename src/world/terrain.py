from dataclasses import dataclass

@dataclass
class Terrain:
    name:str
    char:str
    resource_max: int
    regen: int
    reserve: int = 0

    def __post_init__(self):
        self.reserve = self.resource_max

    def regenerate(self):
        self.reserve = min(self.resource_max, self.reserve + self.regen)

    def take_damage(self, amount:int)->int:
        actual=min(amount, self.reserve)
        self.reserve -= actual
        return actual

    def copy(self)->"Terrain":
        t=Terrain(self.name, self.char, self.resource_max, self.regen, self.reserve)
        t.reserve=self.resource_max
        return t