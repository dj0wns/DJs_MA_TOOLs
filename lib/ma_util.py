import jsonpickle
import json
import math
import struct
from . import init_classes

# for building elements without constructor - probably should have written my constructors different but it is what it is
class Empty(object):
  pass

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
  init.data['pointer_to_game_data'] = -1
  return init

def default_mesh_shape():
  shape = Empty()
  shape.__class__ = init_classes.ShapeData
  shape.data = {}
  shape.shape_type = "FWORLD_SHAPETYPE_MESH"
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

def add_table_to_gamedata(gamedata, table_name, values, var_type):
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
  for value in values:
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


  
