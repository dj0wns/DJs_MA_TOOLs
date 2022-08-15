from .base import Loader
from .csv import CSVLoader

DEFAULT_LOADER = Loader
LOADERS = {
    'csv': CSVLoader,
}


def get_loader(ext, disable_formatting):
    if disable_formatting:
      return DEFAULT_LOADER
    if ext not in LOADERS:
        return DEFAULT_LOADER
    return LOADERS[ext]
