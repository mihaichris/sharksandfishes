from mpi4py import MPI
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from app.models.fish import Fish
from app.models.shark import Shark
import numpy
import random

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()


class World:
    EMPTY_CELL = 0
    FISH_CELL = 1
    SHARK_CELL = 2
    WATER_COLOR = '#00008b'
    SHARK_COLOR = '#ff69b4'
    FISH_COLOR = '#00cc00'

    def __init__(self, length: int, width: int, height: int):
        self.length = length
        self.width = width
        self.height = height
        self.creatures = list()
        self.cube = self.init_empty_cube(self)
        self.number_cells = length * width * height
        self.number_fishes = 0
        self.number_sharks = 0

    def spawn_fish(self, x: int, y: int, z: int):
        fish: Fish = Fish(x, y, z)
        self.creatures.append(fish)
        self.cube[x, y, z] = fish

    def spawn_shark(self, x: int, y: int, z: int):
        shark: Shark = Shark(x, y, z)
        self.creatures.append(shark)
        self.cube[x, y, z] = shark

    def place_fishes(self, number_fishes: int):
        range_down = self.width
        range_up = 0
        if rank is not size - 1:
            range_down = self.width - 1
        if rank is not 1:
            range_up = 1

        for i in range(number_fishes):
            while True:
                x = random.randrange(0, self.length)
                y = random.randrange(range_up, range_down)
                z = random.randrange(0, self.height)
                if not self.cube[x, y, z]:
                    self.spawn_fish(x, y, z)
                    break

    def place_sharks(self, number_sharks):
        range_down = self.width
        range_up = 0
        if rank is not size - 1:
            range_down = self.width - 1
        if rank is not 1:
            range_up = 1

        for i in range(number_sharks):
            while True:
                x = random.randrange(0, self.length)
                y = random.randrange(range_up, range_down)
                z = random.randrange(0, self.height)
                if not self.cube[x, y, z]:
                    self.spawn_shark(x, y, z)
                    break

    def populate_world(self, number_fishes, number_sharks):
        self.number_fishes = number_fishes
        self.number_sharks = number_sharks
        self.place_fishes(self.number_fishes)
        self.place_sharks(self.number_sharks)

    def get_world_cube_image(self):
        cells = numpy.zeros((self.length, self.width, self.height), dtype=int)
        cells_colors = numpy.empty(cells.shape, dtype=object)
        for index, cell in numpy.ndenumerate(self.cube):
            x, y, z = index
            if self.cube[x, y, z] is not self.EMPTY_CELL:
                if isinstance(self.cube[x, y, z], Fish):
                    cells[x, y, z] = self.FISH_CELL
                    cells_colors[x, y, z] = self.FISH_COLOR
                else:
                    cells[x, y, z] = self.SHARK_CELL
                    cells_colors[x, y, z] = self.SHARK_COLOR
            else:
                cells[x, y, z] = self.EMPTY_CELL
                cells_colors[x, y, z] = self.WATER_COLOR
        return cells_colors, cells

    def get_world_image(self):
        world_cube_colors, world_cube_image = self.get_world_cube_image()
        figure = plt.figure()
        ax = figure.gca(projection='3d')
        ax.voxels(world_cube_image, facecolors=world_cube_colors, edgecolor='k')
        return figure

    def show_world(self):
        figure = self.get_world_image()
        plt.show(block=False)
        plt.close(figure)

    def save_world(self, filename):
        figure = self.get_world_image()
        plt.savefig(filename, dpi=72, bbox_inches='tight', pad_inches=0)
        plt.close(figure)

    def get_creature_neighbours(self, creature):
        neighbours = list()

        neighbours.append((self.cube[creature.x][creature.y][
                               creature.z + 1] if creature.z + 1 < self.height else None,
                           (creature.x, creature.y, creature.z + 1)))
        neighbours.append((self.cube[creature.x][creature.y][
                               creature.z - 1] if creature.z - 1 >= 0 else None,
                           (creature.x, creature.y, creature.z - 1)))
        neighbours.append((self.cube[creature.x][creature.y + 1][
                               creature.z] if creature.y + 1 < self.width else None,
                           (creature.x, creature.y + 1, creature.z)))
        neighbours.append((self.cube[creature.x][creature.y - 1][
                               creature.z] if creature.y - 1 >= 0 else None,
                           (creature.x, creature.y - 1, creature.z)))
        neighbours.append((self.cube[creature.x + 1][creature.y][
                               creature.z] if creature.x + 1 < self.length else None,
                           (creature.x + 1, creature.y, creature.z)))
        neighbours.append((self.cube[creature.x - 1][creature.y][
                               creature.z] if creature.x - 1 >= 0 else None,
                           (creature.x - 1, creature.y, creature.z)))
        neighbours.append((self.cube[creature.x][creature.y + 1][
                               creature.z - 1] if creature.y + 1 < self.width and creature.z - 1 >= 0 else None,
                           (creature.x, creature.y + 1, creature.z - 1)))
        neighbours.append((self.cube[creature.x][creature.y + 1][
                               creature.z + 1] if creature.y + 1 < self.width and creature.z + 1 < self.height else None,
                           (creature.x, creature.y + 1, creature.z + 1)))
        neighbours.append((self.cube[creature.x][creature.y - 1][
                               creature.z - 1] if creature.y - 1 >= 0 and creature.z - 1 >= 0 else None,
                           (creature.x, creature.y - 1, creature.z - 1)))
        neighbours.append((self.cube[creature.x][creature.y - 1][
                               creature.z + 1] if creature.y - 1 >= 0 and creature.z + 1 < self.height else None,
                           (creature.x, creature.y - 1, creature.z + 1)))
        neighbours.append((self.cube[creature.x + 1][creature.y + 1][
                               creature.z] if creature.x + 1 < self.length and creature.y + 1 < self.width else None,
                           (creature.x + 1, creature.y + 1, creature.z)))
        neighbours.append((self.cube[creature.x + 1][creature.y - 1][
                               creature.z] if creature.x + 1 < self.length and creature.y - 1 >= 0 else None,
                           (creature.x + 1, creature.y - 1, creature.z)))
        neighbours.append((self.cube[creature.x + 1][creature.y][
                               creature.z - 1] if creature.x + 1 < self.length and creature.z - 1 >= 0 else None,
                           (creature.x + 1, creature.y, creature.z - 1)))
        neighbours.append((self.cube[creature.x + 1][creature.y][
                               creature.z + 1] if creature.x + 1 < self.length and creature.z + 1 < self.height else None,
                           (creature.x + 1, creature.y, creature.z + 1)))
        neighbours.append((self.cube[creature.x - 1][creature.y + 1][
                               creature.z] if creature.x - 1 >= 0 and creature.y + 1 < self.width else None,
                           (creature.x - 1, creature.y + 1, creature.z)))
        neighbours.append((self.cube[creature.x - 1][creature.y - 1][
                               creature.z] if creature.x - 1 >= 0 and creature.y - 1 >= 0 else None,
                           (creature.x - 1, creature.y - 1, creature.z)))
        neighbours.append((self.cube[creature.x - 1][creature.y][
                               creature.z - 1] if creature.x - 1 >= 0 and creature.z - 1 >= 0 else None,
                           (creature.x - 1, creature.y, creature.z - 1)))
        neighbours.append((self.cube[creature.x - 1][creature.y][
                               creature.z + 1] if creature.x - 1 >= 0 and creature.z + 1 < self.height else None,
                           (creature.x - 1, creature.y, creature.z + 1)))
        neighbours.append((self.cube[creature.x + 1][creature.y + 1][
                               creature.z - 1] if creature.x + 1 < self.length and creature.y + 1 < self.width and creature.z - 1 >= 0 else None,
                           (creature.x + 1, creature.y + 1, creature.z - 1)))
        neighbours.append((self.cube[creature.x + 1][creature.y + 1][
                               creature.z + 1] if creature.x + 1 < self.length and creature.y + 1 < self.width and creature.z + 1 < self.height else None,
                           (creature.x + 1, creature.y + 1, creature.z + 1)))
        neighbours.append((self.cube[creature.x + 1][creature.y - 1][
                               creature.z - 1] if creature.x + 1 < self.length and creature.y - 1 >= 0 and creature.z - 1 >= 0 else None,
                           (creature.x + 1, creature.y - 1, creature.z - 1)))
        neighbours.append((self.cube[creature.x + 1][creature.y - 1][
                               creature.z + 1] if creature.x + 1 < self.length and creature.y - 1 >= 0 and creature.z + 1 < self.height else None,
                           (creature.x + 1, creature.y - 1, creature.z + 1)))
        neighbours.append((self.cube[creature.x - 1][creature.y + 1][
                               creature.z - 1] if creature.x - 1 >= 0 and creature.y + 1 < self.width and creature.z - 1 >= 0 else None,
                           (creature.x - 1, creature.y + 1, creature.z - 1)))
        neighbours.append((self.cube[creature.x - 1][creature.y + 1][
                               creature.z + 1] if creature.x - 1 >= 0 and creature.y + 1 < self.width and creature.z + 1 < self.height else None,
                           (creature.x - 1, creature.y + 1, creature.z + 1)))
        neighbours.append((self.cube[creature.x - 1][creature.y - 1][
                               creature.z - 1] if creature.x - 1 >= 0 and creature.y - 1 >= 0 and creature.z - 1 >= 0 else None,
                           (creature.x - 1, creature.y - 1, creature.z - 1)))
        neighbours.append((self.cube[creature.x - 1][creature.y - 1][
                               creature.z + 1] if creature.x - 1 >= 0 and creature.y - 1 >= 0 and creature.z + 1 < self.height else None,
                           (creature.x - 1, creature.y - 1, creature.z + 1)))

        return neighbours

    def evolve_world(self):
        random.shuffle(self.creatures)
        number_creatures = len(self.creatures)
        for i in range(number_creatures):
            creature = self.creatures[i]
            if creature.is_dead():
                continue
            if isinstance(creature, Shark):
                self.evolve_shark(creature)
            else:
                self.evolve_fish(creature)
        self.creatures = [creature for creature in self.creatures
                          if not creature.is_dead()]

    def evolve_fish(self, creature):
        neighbours = self.get_creature_neighbours(creature)
        creature.fertility += 1
        creature.energy -= 1
        if creature.energy < 0:
            creature.state = creature.DEAD
            self.cube[creature.x][creature.y][creature.z] = self.EMPTY_CELL
            return
        moved = False
        empty_cells = [cell for cell in neighbours if cell[0] == self.EMPTY_CELL]
        try:
            empty_cell = random.choice(empty_cells)
            xp = empty_cell[1][0]
            yp = empty_cell[1][1]
            zp = empty_cell[1][2]
            moved = True
        except IndexError:
            xp, yp, zp = creature.x, creature.y, creature.z

        if moved:
            x, y, z = creature.x, creature.y, creature.z
            creature.x, creature.y, creature.z = xp, yp, zp
            self.cube[xp][yp][zp] = creature
            if creature.fertility >= creature.FERTILITY_THRESHOLD:
                creature.fertility = 0
                self.spawn_fish(x, y, z)
            else:
                self.cube[x][y][z] = self.EMPTY_CELL

    def evolve_shark(self, creature):
        neighbours = self.get_creature_neighbours(creature)
        creature.fertility += 1
        creature.energy -= 1
        if creature.energy < 0:
            creature.state = creature.DEAD
            self.cube[creature.x][creature.y][creature.z] = self.EMPTY_CELL
            return
        moved = False
        fishes = [cell[0] for cell in neighbours if isinstance(cell[0], Fish) is True]
        try:
            fish = random.choice(fishes)
            moved = True
            creature.energy += 1
            self.cube[fish.x][fish.y][fish.z].state = fish.DEAD
            self.cube[fish.x][fish.y][fish.z] = self.EMPTY_CELL
            xp = fish.x
            yp = fish.y
            zp = fish.z
        except IndexError:
            pass

        if not moved:
            empty_cells = [cell for cell in neighbours if cell[0] == self.EMPTY_CELL]
            try:
                empty_cell = random.choice(empty_cells)
                xp = empty_cell[1][0]
                yp = empty_cell[1][1]
                zp = empty_cell[1][2]
                moved = True
            except IndexError:
                xp, yp, zp = creature.x, creature.y, creature.z

        if moved:
            x, y, z = creature.x, creature.y, creature.z
            creature.x, creature.y, creature.z = xp, yp, zp
            self.cube[xp][yp][zp] = creature
            if creature.fertility >= creature.FERTILITY_THRESHOLD:
                creature.fertility = 0
                self.spawn_shark(x, y, z)
            else:
                self.cube[x][y][z] = self.EMPTY_CELL

    def merge_creatures_positions_from_up(self, data):
        for x in range(self.length):
            for z in range(self.height):
                if self.cube[x, self.width - 2, z] is self.EMPTY_CELL:
                    self.cube[x, self.width - 2, z] = data[x, 0, z]
                elif (isinstance(self.cube[x, self.width - 2, z], Shark) or isinstance(self.cube[x, self.width - 2, z],
                                                                                       Fish)) and isinstance(
                    data[x, 0, z], Fish):
                    creature = self.cube[x, self.width - 2, z]
                    creature.x, creature.y, creature.z = x, self.width - 2, z
                    neighbours = self.get_creature_neighbours(creature)
                    empty_cells = [cell for cell in neighbours if cell[0] == self.EMPTY_CELL]
                    try:
                        empty_cell = random.choice(empty_cells)
                        xp = empty_cell[1][0]
                        yp = empty_cell[1][1]
                        zp = empty_cell[1][2]
                        self.cube[xp, yp, zp] = data[x, 0, z]
                    except IndexError:
                        pass
                elif isinstance(self.cube[x, self.width - 2, z], Fish) and isinstance(data[x, 0, z],
                                                                                      Shark):
                    self.cube[x, self.width - 2, z] = data[x, 0, z]

    def merge_creatures_positions_from_down(self, data):
        for x in range(self.length):
            for z in range(self.height):
                if self.cube[x, 1, z] is self.EMPTY_CELL:
                    self.cube[x, 1, z] = data[x, data.shape[1] - 1, z]
                elif (isinstance(self.cube[x, 1, z], Shark) or isinstance(
                        self.cube[x, 1, z], Fish)) and isinstance(data[x, data.shape[1] - 1, z], Fish):
                    creature = self.cube[x, 1, z]
                    creature.x, creature.y, creature.z = x, 1, z
                    neighbours = self.get_creature_neighbours(self.cube[x, 1, z])
                    empty_cells = [cell for cell in neighbours if cell[0] == self.EMPTY_CELL]
                    try:
                        empty_cell = random.choice(empty_cells)
                        xp = empty_cell[1][0]
                        yp = empty_cell[1][1]
                        zp = empty_cell[1][2]
                        self.cube[xp, yp, zp] = data[x, data.shape[1] - 1, z]
                    except IndexError:
                        pass
                elif isinstance(self.cube[x, 1, z], Fish) and isinstance(data[x, data.shape[1] - 1, z],
                                                                         Shark):
                    self.cube[x, 1, z] = data[x, data.shape[1] - 1, z]

    @staticmethod
    def init_empty_cube(self):
        return numpy.zeros((self.length, self.width, self.height), dtype=object)
