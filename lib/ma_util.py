import jsonpickle
import json
import math
import struct

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
