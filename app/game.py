import time
import numpy
import threading
from mpi4py import MPI

from app.models.fish import Fish
from app.models.shark import Shark
from app.models.world import World
from setup import MPILogger, DebugLogger, DATA_DIR, MAX_GENERATIONS, WORLD_LENGTH, WORLD_WIDTH, WORLD_HEIGHT

comm = MPI.COMM_WORLD
size: int = comm.Get_size()
rank: int = comm.Get_rank()


class Game:
    def __init__(self, world_length: int, world_width: int, world_height: int, fish_number: int, sharks_number: int):
        self.world_length = world_length
        self.world_width = world_width
        self.world_height = world_height
        self.fish_number = fish_number
        self.sharks_number = sharks_number
        self.process_start_time = time.process_time()
        self.threads = list()

        if rank is 0:
            world = World(WORLD_LENGTH, WORLD_WIDTH, WORLD_HEIGHT)
        else:
            world = World(self.world_length, self.world_width, self.world_height)
            world.populate_world(self.fish_number, self.sharks_number)
            self.update_initial_ghost_borders(world)

        for generation in range(MAX_GENERATIONS):
            world_cube = world.cube
            gathered_cubes = comm.gather(world_cube, root=0)
            if rank is 0:
                thread = threading.Thread(target=self.save_game(generation, world, gathered_cubes), daemon=True)
                # thread.start()
            else:
                MPILogger.info('Process {} started to update borders.'.format(rank))
                self.update_ghost_borders(world)
                world.evolve_world()

    def update_ghost_borders(self, world: World) -> None:
        if rank is not size - 1:
            # Start sending down
            to_down_data = numpy.zeros((self.world_length, self.world_width, self.world_height), dtype=object)
            to_down_data[:self.world_length, 0, :self.world_height] = world.cube[:self.world_length, 0,
                                                                      :self.world_height]
            comm.send(to_down_data, dest=rank + 1, tag=10)
            # End sending down

        if rank is not 1:
            # Start receiving from up
            from_up_data = comm.recv(source=rank - 1, tag=10)
            # End receiving from up
            world.merge_creatures_positions_from_up(from_up_data)

        if rank is not 1:
            # Start sending to up
            to_up_data = numpy.zeros((self.world_length, self.world_width, self.world_height), dtype=object)
            to_up_data[:self.world_length, self.world_width - 1, :self.world_height] = world.cube[:self.world_length,
                                                                                       self.world_width - 1,
                                                                                       :self.world_height]
            comm.send(to_up_data, dest=rank - 1, tag=10)
            # End sending to up

        if rank is not size - 1:
            # Start receiving from down
            from_down_data = comm.recv(source=rank + 1, tag=10)
            # End receiving from down
            world.merge_creatures_positions_from_down(from_down_data)

        world.creatures = []
        world.number_fishes = 0
        world.number_sharks = 0
        for index, creature in numpy.ndenumerate(world.cube):
            if isinstance(creature, Fish) or isinstance(creature, Shark):
                creature.x = index[0]
                creature.y = index[1]
                creature.z = index[2]
                world.creatures.append(creature)
                if isinstance(creature, Fish):
                    world.number_fishes += 1
                else:
                    world.number_sharks += 1

    def update_initial_ghost_borders(self, world: World) -> None:
        if rank is not size - 1:
            # Start sending down
            to_down_data = numpy.zeros((self.world_length, self.world_width, self.world_height), dtype=numpy.object)
            to_down_data[:self.world_length, 1, :self.world_height] = world.cube[:self.world_length, 1,
                                                                      :self.world_height]
            comm.send(to_down_data, dest=rank + 1, tag=11)
            # End sending down

        if rank is not 1:
            # Start receiving from up
            from_up_data = comm.recv(source=rank - 1, tag=11)
            world.cube[:self.world_length, self.world_width - 1, :self.world_height] = from_up_data[:self.world_length,
                                                                                       1,
                                                                                       :self.world_height]
            # End receiving from up

        if rank is not 1:
            # Start sending to up
            to_up_data = numpy.zeros((self.world_length, self.world_width, self.world_height), dtype=numpy.object)
            to_up_data[:self.world_length, self.world_width - 2, :self.world_height] = world.cube[:self.world_length,
                                                                                       self.world_width - 2,
                                                                                       :self.world_height]
            comm.send(to_up_data, dest=rank - 1, tag=11)
            # End sending to up

        if rank is not size - 1:
            # Start receiving from down
            from_down_data = comm.recv(source=rank + 1, tag=11)
            world.cube[:self.world_length, 0, :self.world_height] = from_down_data[:self.world_length,
                                                                    self.world_width - 2,
                                                                    :self.world_height]
            # End receiving from down

        # world.creatures = []
        # world.number_fishes = 0
        # world.number_sharks = 0
        # for index, creature in numpy.ndenumerate(world.cube):
        #     if isinstance(creature, Fish) or isinstance(creature, Shark):
        #         creature.x = index[0]
        #         creature.y = index[1]
        #         creature.z = index[2]
        #         world.creatures.append(creature)
        #         if isinstance(creature, Fish):
        #             world.number_fishes += 1
        #         else:
        #             world.number_sharks += 1

    def save_game(self, generation, world, gathered_cubes):
        DebugLogger.info('Thread for generation: {} started'.format(generation))
        worlds_cubes = []
        for index, gathered_cube in enumerate(gathered_cubes[1:], start=1):
            if index == 1:
                gathered_cube = numpy.delete(gathered_cube, self.world_width // (size - 1), axis=1)
            elif index == (size - 1):
                gathered_cube = numpy.delete(gathered_cube, 0, axis=1)
            else:
                gathered_cube = numpy.delete(gathered_cube, 0, axis=1)
                gathered_cube = numpy.delete(gathered_cube, self.world_width // (size - 1), axis=1)
            worlds_cubes.append(gathered_cube)
        cube = numpy.concatenate(worlds_cubes, axis=1)
        world.cube = cube

        # Start reset world creatures for rank 0
        world.creatures = []
        world.number_fishes = 0
        world.number_sharks = 0
        for index, creature in numpy.ndenumerate(cube):
            if isinstance(creature, Fish) or isinstance(creature, Shark):
                creature.x = index[0]
                creature.y = index[1]
                creature.z = index[2]
                world.creatures.append(creature)
                if isinstance(creature, Fish):
                    world.number_fishes += 1
                else:
                    world.number_sharks += 1
        # End reset world creatures for rank 0
        DebugLogger.debug(
            'Generation {}/{}: Fishes: {}, Sharks: {}'.format(generation + 1, MAX_GENERATIONS, world.number_fishes,
                                                              world.number_sharks))
        print('Generation {}/{}: Creatures: {}'.format(generation + 1, MAX_GENERATIONS, len(world.creatures)))
        world.save_world(DATA_DIR + '/world-{:04d}.png'.format(generation + 1))
        DebugLogger.info('Thread for generation: {} saved the world'.format(generation + 1))
