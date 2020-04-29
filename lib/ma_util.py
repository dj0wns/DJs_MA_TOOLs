import jsonpickle
import json
import math
import struct
import os
from . import init_classes

# for building elements without constructor - probably should have written my constructors different but it is what it is
class Empty(object):
  pass
 
class init_shape_game_data:
  def __init__(self):
    self.init = None
    self.gamedata = None
    self.shape = None
  def set_init(self, init):
    self.init = init
  def set_gamedata(self, gamedata):
    self.gamedata = gamedata
  def set_shape(self, shape):
    self.shape = shape

def wld_folder_to_init_shape_gamedata(directory) :
  init_shape_game_data_dict = {}
  init_shape_game_data_list = []
  for filename in os.listdir(directory):
    filepath = os.path.join(directory, filename)
    if filename == "preinit.dat":
      preinit = open(filepath, "rb").read()
    elif filename == "header.json":
      header_packed = open(filepath, "rb").read()
      header = jsonpickle.decode(header_packed)
    elif filename == "init_header.json":
      init_header_packed = open(filepath, "rb").read()
      init_header = jsonpickle.decode(init_header_packed)
    elif "_init_object." in filename:
      init_object_packed = open(filepath, "rb").read()
      if filename.split("_")[0] not in init_shape_game_data_dict:
        init_shape_game_data_dict[filename.split("_")[0]] = init_shape_game_data()
      init_shape_game_data_dict[filename.split("_")[0]].set_init(jsonpickle.decode(init_object_packed))

    elif "_shape." in filename:
      shape_packed = open(filepath, "rb").read()
      if filename.split("_")[0] not in init_shape_game_data_dict:
        init_shape_game_data_dict[filename.split("_")[0]] = init_shape_game_data()
      init_shape_game_data_dict[filename.split("_")[0]].set_shape(jsonpickle.decode(shape_packed))
      #TODO Remove this hack - just zeroing out the color streams to see what happens and so you can edit campaign levels - This works with minor color errors so calling it a win until we can parse meshes
      if init_shape_game_data_dict[filename.split("_")[0]].shape.shape_type == "FWORLD_SHAPETYPE_MESH":
        init_shape_game_data_dict[filename.split("_")[0]].shape.data['mesh'].color_stream_count = 0
        init_shape_game_data_dict[filename.split("_")[0]].shape.data['mesh'].color_stream_offset = 0
        init_shape_game_data_dict[filename.split("_")[0]].shape.data['mesh'].flags = 0

    elif "_gamedata." in filename:
      gamedata = Empty()
      gamedata.__class__ = init_classes.GameDataHeader
      gamedata_json = open(filepath, "r").read()
      gamedata.from_json(gamedata_json)
      if filename.split("_")[0] not in init_shape_game_data_dict:
        init_shape_game_data_dict[filename.split("_")[0]] = init_shape_game_data()
      init_shape_game_data_dict[filename.split("_")[0]].set_gamedata(gamedata)

  #set dict to list form - should have used a dict earlier but dont want to rewrite it
  #sort the keys
  for key in sorted(init_shape_game_data_dict):
    init_shape_game_data_list.append([init_shape_game_data_dict[key].init, init_shape_game_data_dict[key].shape, init_shape_game_data_dict[key].gamedata])

  init_header.data['item_count'] = len(init_shape_game_data_list)
  return preinit, header, init_header, init_shape_game_data_list



def roundup(x):
  return int(math.ceil(x / 16.0)) * 16

def roundup_4(x):
  return int(math.ceil(x / 4.0)) * 4

def roundup_2(x):
  return int(math.ceil(x / 2.0)) * 2

def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False

def pretty_json(string):
  dump = json.dumps(json.loads(string), indent=4, sort_keys=False)
  #print(str(dump))
  return dump

def pretty_pickle_json(to_pack):
  encoded = jsonpickle.encode(to_pack)
  return pretty_json(encoded)
 
class Vector:
  def __init__(self,dimensions=0,x=0,y=0,z=3):
    self.dimensions = dimensions
    self.x = x
    self.y = y
    self.z = z
  
  def print_data(self):
    print("Vector:")
    print("x: ", self.x)
    print("y: ", self.y)
    print("z: ", self.z)

  def to_bytes(self, float_endian):
    raw = struct.pack(float_endian, self.x)
    raw += struct.pack(float_endian, self.y)
    raw += struct.pack(float_endian, self.z)
    return raw
