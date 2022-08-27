from app.models.creature import Creature


class Shark(Creature):
    FERTILITY_THRESHOLD = 12
    ENERGY: int = 3

    def __init__(self, x: int, y: int, z: int):
        super().__init__(x, y, z)
        self.energy = self.ENERGY
