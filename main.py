from spman import *
from player import *

if __name__ == '__main__':
    library = []

    print('Fetching library')
    for lib_batch in get_library():
        library.extend(lib_batch)

    print('Saving library')
    save_library(library)
    exit()

    print('Starting Shuffle')
    start_shuffle(library)
