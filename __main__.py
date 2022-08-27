from app.game import Game
from mpi4py import MPI
from setup import MPILogger, WORLD_LENGTH, WORLD_WIDTH, WORLD_HEIGHT, SHARKS_NUMBER, FISH_NUMBER
import time

if __name__ == '__main__':

    comm = MPI.COMM_WORLD
    size: int = comm.Get_size()
    rank: int = comm.Get_rank()
    name: str = MPI.Get_processor_name()
    if rank is 0:
        MPILogger.info('Rank : {} from processor: {} will be used for managing other processes.'.format(rank, name))
    try:
        assert WORLD_WIDTH % (size - 1) == 0
    except AssertionError:
        print('Number of processes are not equally divided.')
        MPILogger.error('Number of processes are not equally divided.')
        exit()

    try:
        assert (WORLD_LENGTH * WORLD_WIDTH * WORLD_HEIGHT) > (SHARKS_NUMBER + FISH_NUMBER)
    except AssertionError:
        print('The world is to small for all the creatures.')
        MPILogger.error('The world is to small for all the creatures.')
        exit()

    if rank is 0:
        MPILogger.info('Starting rank: {} to partition data to other processes.'.format(rank))
        for process in range(1, size):
            world_length: int = WORLD_LENGTH
            world_width: int = (WORLD_WIDTH // (size - 1)) + 2
            world_height: int = WORLD_HEIGHT
            fishes_number: int = FISH_NUMBER // (size - 1)
            sharks_number: int = SHARKS_NUMBER // (size - 1)
            data = {'length': world_length,
                    'width': world_width,
                    'height': world_height,
                    'fishes': fishes_number,
                    'sharks': sharks_number
                    }
            comm.send(data, dest=process, tag=9)
            MPILogger.info('Data send to process {}.'.format(process))
        game = Game(WORLD_LENGTH, WORLD_WIDTH, WORLD_HEIGHT, FISH_NUMBER, SHARKS_NUMBER)
        process_start_time = game.process_start_time
        process_stop_time = time.process_time()
        print('The process duration was: {}'.format(process_stop_time - process_start_time))
    else:
        data = comm.recv(source=0, tag=9)
        MPILogger.info('Process {} received data from process 0.'.format(rank))
        if rank in [1, size - 1]:
            game = Game(data['length'], data['width'] - 1, data['height'], data['fishes'], data['sharks'])
        else:
            game = Game(data['length'], data['width'], data['height'], data['fishes'], data['sharks'])
