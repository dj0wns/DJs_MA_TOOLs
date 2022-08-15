from enum import Enum
import datetime

try:
  from ..mst_loaders import get_loader
except:
  from mst_loaders import get_loader

from .misc import BinaryIO, ProtocolException


class GamePlatform(Enum):
  xbox = 0
  playstation = 1
  gamecube = 2


class MST:
  def __init__(self):
    self.platform = None
    self.package_size = 0
    self.file_count = 0
    self.unknown_bitmask = 0
    self.suffix_unknowns = []
    self.files = []

  def __repr__(self):
    return 'MST({}, {} bytes, {} files)'.format(self.platform, self.package_size, self.file_count)

  def read(self, reader: BinaryIO, disable_formatting):
    header = reader.read_str(4) # FANG
    if header == 'FANG': # Xbox, PS2
      reader.little_endian = True
    elif header == 'GNAF':
      reader.little_endian = False
      self.platform = GamePlatform.gamecube
    else:
      raise ProtocolException()

    self.unknown_bitmask, self.package_size, self.file_count = reader.read_fmt('III')
    self.suffix_unknowns = reader.read_fmt('I' * 23)

    if reader.little_endian:
      # no idea what this is, but seems to be 3 in PS2 builds, 2 in Xbox & GC
      platform_id = self.suffix_unknowns[14]
      print(platform_id)
      if platform_id == 3:
        self.platform = GamePlatform.playstation
      elif platform_id == 2:
        self.platform = GamePlatform.xbox
      else:
        raise ProtocolException()

    self.files = []
    for i in range(self.file_count):
      file = MSTEntry()
      file.read(reader, self.platform, disable_formatting)
      self.files.append(file)
    return reader.little_endian



class MSTEntry:
  def __init__(self):
    self.name = None
    self.location = 0
    self.length = 0
    self.create_date = None
    self.unknown = 0
    self.loader = None

  def read(self, reader: BinaryIO, platform: GamePlatform, disable_formatting):
    name_length = 24 if platform == GamePlatform.playstation else 20
    self.name = reader.read_str(name_length).split('\0')[0] # important to re-add this when writing
    self.location, self.length, timestamp, self.unknown = reader.read_fmt('IIII')
    self.create_date = datetime.date.fromtimestamp(timestamp)
    ext = self.name.split('.')[-1].lower()
    self.loader = get_loader(ext, disable_formatting)(self)
