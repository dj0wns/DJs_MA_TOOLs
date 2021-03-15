import jsonpickle
import json
import math
import struct
import os
from . import init_classes

level_names = [
  "Hero Training",
  "Do Ore Die",
  "Seal The Mines",
  "Clean Up",
  "Wasteland Thunder",
  "They Live",
  "Wasteland Journey",
  "Mozer, Schmozer",
  "The ZombieBot King",
  "Into The Trenches",
  "Infiltrate The Compound",
  "Destroy Comm Arrays",
  "Hold Your Ground",
  "What Research?",
  "The Search For Krunk",
  "F&!?ing Krunked",
  "You Know The Drill",
  "Wasteland Chase",
  "Morbot City",
  "I, Predator",
  "The Reactor Core",
  "Fire it Up",
  "The Hand Is Mightier",
  "Find The Spy Factory",
  "Unhandled Exception",
  "Access The Ruins",
  "Seen Better Days",
  "The Sniper's Lair",
  "Secret Rendezvous",
  "Bright Lights, Mil City",
  "Get To The Tower",
  "Unwelcome Home",
  "15 Minutes",
  "Round 2",
  "Last Bot Standing",
  "Fall To Pieces",
  "Race To The Rocket",
  "One Small Step",
  "Fully Operational",
  "Bring It Down",
  "General Corrosive",
  "Final Battle"]

item_tag_names = [
  "washer",
  "chip",
  "secret chip",
  "det pack",
  "arm servo",
  "goff part",
  "null primary",
  "null secondary",
  "null item",
  "sprim",
  "sseco",
  "empty primary",
  "empty secondary",
  "rivet gun l1",
  "rivet gun l2",
  "rivet gun l3",
  "laser l1",
  "laser l2",
  "laser l3",
  "laser mil l1",
  "coring charge",
  "coring charge mil possessed",
  "rlauncher l1",
  "rlauncher l2",
  "rlauncher l3",
  "blaster l1",
  "blaster l2",
  "blaster l3",
  "tether l1",
  "tether l2",
  "tether l3",
  "tether krunk",
  "spew l1",
  "spew l2",
  "spew l3",
  "spew mil l1",
  "mortar l1",
  "ripper l1",
  "ripper l2",
  "ripper l3",
  "flamer l1",
  "cleaner",
  "scope l1",
  "scope l2",
  "emp grenade",
  "magma bomb",
  "recruiter grenade",
  "wrench",
]

# for building elements without constructor - probably should have written my constructors different but it is what it is
class Empty(object):
  pass
 
class init_shape_game_data:
  def __init__(self):
    self.init = None
    self.gamedata = None
    self.shape = None
    self.name = None
  def set_init(self, init):
    self.init = init
  def set_gamedata(self, gamedata):
    self.gamedata = gamedata
  def set_shape(self, shape):
    self.shape = shape
  def set_name(self, name):
    self.name = name

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
      init_shape_game_data_dict[filename.split("_")[0]].set_name(filename.split("_")[0])

    elif "_shape." in filename:
      shape_packed = open(filepath, "rb").read()
      if filename.split("_")[0] not in init_shape_game_data_dict:
        init_shape_game_data_dict[filename.split("_")[0]] = init_shape_game_data()
      init_shape_game_data_dict[filename.split("_")[0]].set_shape(jsonpickle.decode(shape_packed))
      #TODO Remove this hack - just zeroing out the color streams to see what happens and so you can edit campaign levels - This works with minor color errors so calling it a win until we can parse meshes
      if init_shape_game_data_dict[filename.split("_")[0]].shape.shape_type == "FWORLD_SHAPETYPE_MESH":
        init_shape_game_data_dict[filename.split("_")[0]].shape.data['mesh'].color_stream_count = 0
        init_shape_game_data_dict[filename.split("_")[0]].shape.data['mesh'].color_stream_offset = 0
        flags = init_shape_game_data_dict[filename.split("_")[0]].shape.data['mesh'].flags
        if flags & 0x80:
          flags -= 0x80
        init_shape_game_data_dict[filename.split("_")[0]].shape.data['mesh'].flags = flags

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
    init_shape_game_data_list.append([init_shape_game_data_dict[key].init, init_shape_game_data_dict[key].shape, init_shape_game_data_dict[key].gamedata, init_shape_game_data_dict[key].name])

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

def default_init():
  init = Empty()
  init.__class__ = init_classes.InitObject
  init.data = {}
  init.data['offset'] = 0
  init.data['shape_type'] = "FWORLD_SHAPETYPE_MESH"
  init.data['shape_offset'] = -1
  #default orientation
  init.data['Right_X'] = 1.
  init.data['Right_Y'] = 0.
  init.data['Right_Z'] = 0.
  init.data['Up_X'] = 0.
  init.data['Up_Y'] = 1.
  init.data['Up_Z'] = 0.
  init.data['Front_X'] = 0.
  init.data['Front_Y'] = 0.
  init.data['Front_Z'] = 1.
  init.data['Position_X'] = 0
  init.data['Position_Y'] = 0
  init.data['Position_Z'] = 0
  init.data['shape_index'] = -1
  init.data['pointer_to_game_data'] = 0
  return init

def default_mesh_shape():
  shape = Empty()
  shape.__class__ = init_classes.ShapeData
  shape.data = {}

  shape.shape_type = "FWORLD_SHAPETYPE_MESH"
  shape.data['offset'] = -1

  shape.data['mesh'] = Empty()
  shape.data['mesh'].__class__ = init_classes.Mesh
  shape.data['mesh'].mesh_offset = -1
  shape.data['mesh'].mesh_name = "goshcrate02"
  shape.data['mesh'].lightmap_names = []
  shape.data['mesh'].lightmap_offsets = [0,0,0,0]
  shape.data['mesh'].lightmap_motifs = [0,0,0,0]
  shape.data['mesh'].flags = 0
  shape.data['mesh'].cull_distance = 1.0000000150474662e+30
  shape.data['mesh'].tint = Empty()
  shape.data['mesh'].tint.__class__ = Vector
  shape.data['mesh'].tint.dimensions = 3
  shape.data['mesh'].tint.x = 1.0
  shape.data['mesh'].tint.y = 1.0
  shape.data['mesh'].tint.z = 1.0
  shape.data['mesh'].color_stream_count = 0
  shape.data['mesh'].color_stream_offset = 0
  return shape

def default_point_shape():
  shape = Empty()
  shape.__class__ = init_classes.ShapeData
  shape.data = {}
  shape.shape_type = "FWORLD_SHAPETYPE_POINT"
  shape.data['offset'] = -1
  return shape

def default_gamedata():
  gamedata = Empty()
  gamedata.__class__ = init_classes.GameDataHeader
  gamedata.data = {}
  gamedata.data['offset'] = -1
  gamedata.data['size'] = -1
  gamedata.data['number_of_tables'] = 0
  gamedata.data['pointer_to_tables'] = 0
  gamedata.data['flags'] = 0
  gamedata.tables=[]
  return gamedata

def add_table_to_gamedata(gamedata, table_name, values, var_types):
  table = Empty()
  table.__class__ = init_classes.GameDataTable
  table.data = {}
  table.fields = []
  table.data['offset'] = -1
  table.data['header_offset'] = -1
  table.data['keystring_pointer'] = -1
  table.data['keystring_length'] = len(table_name)
  table.data['num_fields'] = len(values)
  table.data['table_index'] = -1
  table.data['field_offset'] = -1
  table.data['keystring'] = table_name.encode('ascii')
  #now add fields
  for value, var_type in zip(values, var_types):
    field = Empty()
    field.__class__ = init_classes.GameDataField
    field.data = {}
    field.data['offset'] = -1
    field.data['data_type'] = var_type
    if var_type == "FLOAT":
      field.data['float'] = value
      field.data['string_length'] = 0
    elif var_type == "STRING":
      field.data['string_pointer'] = -1
      field.data['string_length'] = len(value)
      field.data['string'] = value.encode('ascii')
    elif var_type == "WIDESTRING":
      field.data['widestring_pointer'] = -1
      field.data['string_length'] = len(value)
      field.data['widestring'] = value.encode('utf-8')
    else:
      print ('INVALID var type')
      return None
    table.fields.append(field)
  gamedata.tables.append(table)
