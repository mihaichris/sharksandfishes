import os
import logging


def logger(name, log_file, level=logging.INFO):
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)
    log = logging.getLogger(name)
    log.setLevel(level)
    log.addHandler(handler)
    return log


ROOT_DIR: str = os.path.dirname(os.path.abspath(__file__))
DATA_DIR: str = os.path.dirname(os.path.abspath(__file__)) + '/data'
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

FISH_NUMBER: int = 1000
SHARKS_NUMBER: int = 200

WORLD_LENGTH: int = 20
WORLD_WIDTH: int = 24
WORLD_HEIGHT: int = 20

MAX_GENERATIONS: int = 20

MPILogger = logger('sharks_and_fishes_mpi_log', 'sharks_and_fishes_mpi.log')
DebugLogger = logger('sharks_and_fishes_debug_log', 'sharks_and_fishes_debug.log', logging.DEBUG)
