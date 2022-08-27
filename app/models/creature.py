class Creature:
    ALIVE = True
    DEAD = False

    def __init__(self, x: int, y: int, z: int):
        self.x = x
        self.y = y
        self.z = z
        self.fertility = 0
        self.energy = 0
        self.state = self.ALIVE

    def is_alive(self) -> bool:
        return self.state is self.ALIVE

    def is_dead(self) -> bool:
        return self.state is self.DEAD

    def get_position(self):
        return self.x, self.y, self.z
