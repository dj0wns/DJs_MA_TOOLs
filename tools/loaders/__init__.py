from .base import Loader
from .csv import CSVLoader
from .tga import TGALoader

DEFAULT_LOADER = Loader
LOADERS = {
    'csv': CSVLoader,
    'tga': TGALoader,
}


def get_loader(ext):
    if ext not in LOADERS:
        return DEFAULT_LOADER
    return LOADERS[ext]
