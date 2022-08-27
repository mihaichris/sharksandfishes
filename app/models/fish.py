from app.models.creature import Creature


class Fish(Creature):
    FERTILITY_THRESHOLD = 4
    ENERGY: int = 20

    def __init__(self, x: int, y: int, z: int):
        super().__init__(x, y, z)
        self.energy = self.ENERGY
