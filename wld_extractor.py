import sys
import os
import shutil
import struct
import math
import json
import jsonpickle
import argparse

#Notes - generates an outfile twice so it can easily fix offsets without having to keep track of where things are

endian='little'
float_endian = '<f'
int_endian = '<i'
short_endian = '<h'

fpath=os.path.realpath(__file__)
py_path=os.path.dirname(fpath)

shape_list = ["FWORLD_SHAPETYPE_POINT",
  "FWORLD_SHAPETYPE_LINE",
  "FWORLD_SHAPETYPE_SPLINE",
  "FWORLD_SHAPETYPE_BOX",
  "FWORLD_SHAPETYPE_SPHERE",
  "FWORLD_SHAPETYPE_CYLINDER",
  "FWORLD_SHAPETYPE_MESH",
  "FWORLD_SHAPETYPE_COUNT"]

shape_value = {"FWORLD_SHAPETYPE_POINT" : 0,
  "FWORLD_SHAPETYPE_LINE" : 1,
  "FWORLD_SHAPETYPE_SPLINE" : 2,
  "FWORLD_SHAPETYPE_BOX" : 3,
  "FWORLD_SHAPETYPE_SPHERE" : 4,
  "FWORLD_SHAPETYPE_CYLINDER" : 5,
  "FWORLD_SHAPETYPE_MESH" : 6,
  "FWORLD_SHAPETYPE_COUNT" : 7}

csv_datatype = [
  "STRING",
  "FLOAT",
  "WIDESTRING",
  "COUNT"]

csv_datavalue = {
  "STRING" : 0,
  "FLOAT" : 1,
  "WIDESTRING" : 2,
  "COUNT" : 3}

# for building elements without constructor - probably should have written my constructors different but it is what it is
class Empty(object):
  pass

def roundup(x):
  return int(math.ceil(x / 16.0)) * 16

def roundup_4(x):
  return int(math.ceil(x / 4.0)) * 4

def pretty_json(string):
  dump = json.dumps(json.loads(string), indent=4, sort_keys=False)
  #print(str(dump))
  return dump

def pretty_pickle_json(to_pack):
  encoded = jsonpickle.encode(to_pack)
  return pretty_json(encoded)

def print_classes(header, initHeader, init_shape_game_data_list):
  header.print_header()
  initHeader.print_header()
  for item in init_shape_game_data_list:
    item[0].print_init()
    item[1].pretty_print()
    if item[2] is not None:
      item[2].pretty_print()


  print("num shape objects: " + str(len(init_shape_game_data_list)))

def parse_wld_file(writer):

  header = Header(writer)
  
  initHeader = InitHeader(writer,header.data['offset_of_inits'])

  init_object_list = []
  init_shape_game_data_list = [] #all the init entries and shapes and game datas refer to the same thing
  for item in range(initHeader.data['item_count']):
    init_object_list.append(InitObject(writer,header.data['offset_of_inits']))

  for item in init_object_list:
    #add offset of init header table + size of init header
    offset = item.data['shape_offset'] + header.data['offset_of_inits'] + 16  #16 byte header
    shape = ShapeData(writer,offset,item.data['shape_type'], header.data['offset_of_inits'] + 16)
    gamedata = None
    if item.data['pointer_to_game_data'] > 0:
      #add offset of init header table + size of init header
      offset = item.data['pointer_to_game_data'] + header.data['offset_of_inits'] + 16  #16 byte header
      gamedata = GameDataHeader(writer,offset)
    init_shape_game_data_list.append([item, shape, gamedata])
  
  return header, initHeader, init_shape_game_data_list

def build_wld_file(path, pre_init_data, initHeader, init_shape_game_data_list, start_of_inits, lightmap_name_locations_dict):
  #rebuild the init section by copying everything else then adding new inits
  
  out_bytes = pre_init_data[:]
  out_bytes += initHeader.to_bytes()

  # shape table before other values
  for item in init_shape_game_data_list:
    out_bytes += item[0].to_bytes()
  
  mesh_name_locations_dict = {} #used so mesh name strings are only used once to match implementation
  
  for item in init_shape_game_data_list:
    #if its a mesh then data is before the shape other wise reverse it
    if item[1].shape_type == "FWORLD_SHAPETYPE_MESH":
      if item[2] is not None:
        #go back and update the shape index as to where you are
        init_relative_offset = len(out_bytes) - start_of_inits
        item[0].data['pointer_to_game_data'] = init_relative_offset
        out_bytes += item[2].to_bytes(init_relative_offset)
      #make sure to align
      out_bytes += bytes(roundup_4(len(out_bytes)) - len(out_bytes))
      #go back and update the shape index as to where you are
      init_relative_offset = len(out_bytes) - start_of_inits
      new_bytes = item[1].to_bytes(mesh_name_locations_dict, lightmap_name_locations_dict, init_relative_offset)
      if new_bytes is not None:
        item[0].data['shape_offset'] = init_relative_offset
        out_bytes += new_bytes
      #always align
      out_bytes += bytes(roundup_4(len(out_bytes)) - len(out_bytes))
    else:
      #go back and update the shape index as to where you are
      init_relative_offset = len(out_bytes) - start_of_inits
      new_bytes = item[1].to_bytes(mesh_name_locations_dict, lightmap_name_locations_dict, init_relative_offset)
      if new_bytes is not None:
        item[0].data['shape_offset'] = init_relative_offset
        out_bytes += new_bytes
      #always align
      out_bytes += bytes(roundup_4(len(out_bytes)) - len(out_bytes))
      if item[2] is not None:
        #go back and update the shape index as to where you are
        init_relative_offset = len(out_bytes) - start_of_inits
        item[0].data['pointer_to_game_data'] = init_relative_offset
        out_bytes += item[2].to_bytes(init_relative_offset)
      #make sure to align
      out_bytes += bytes(roundup_4(len(out_bytes)) - len(out_bytes))

  out_bytes = bytearray(out_bytes)
  
  #add lightmap names at end
  for key, value in lightmap_name_locations_dict.items():
    #update value
    lightmap_name_locations_dict[key] = len(out_bytes) - start_of_inits
    out_bytes += bytearray(key.encode('ascii'))
    #add a null byte
    out_bytes.append(0x0)
    

  #update file size
  size_bytes = struct.pack(int_endian, len(out_bytes))
  for i in range(len(size_bytes)):
    out_bytes[i] = size_bytes[i]


  #update init size
  init_bytes = bytearray()
  for i in range(4):
    init_bytes.append(out_bytes[36+i])
  init_value = int.from_bytes(init_bytes, byteorder=endian, signed=False)
  init_size = struct.pack(int_endian, len(out_bytes) - init_value)
  for i in range(len(init_size)):
    out_bytes[40+i] = init_size[i]

  outfile = open(path, "wb")
  outfile.write(out_bytes)
  outfile.close()

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

def import_from_folder(directory): 
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
        
    elif "_gamedata." in filename:
      gamedata = Empty()
      gamedata.__class__ = GameDataHeader
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

#this takes all values and makes a folder and sticks them in it
def extract_to_file(writer, out_path, header, init_header, init_shape_game_data_list):
  #rebuild the init section by copying everything else then adding new inits
  writer.seek(0)
  pre_init_data = bytearray(writer.read(header.data['offset_of_inits']))
  
  os.mkdir(out_path)

  preinitdata_file = open(os.path.join(out_path, "preinit.dat"), "wb")
  preinitdata_file.write(pre_init_data)
  preinitdata_file.close()
  
  header_file = open(os.path.join(out_path, "header.json"), "w")
  header_file.write(pretty_pickle_json(header))
  header_file.close()

  init_header_file = open(os.path.join(out_path, "init_header.json"), "w")
  init_header_file.write(pretty_pickle_json(init_header))
  init_header_file.close()

  i = 0
  for item in init_shape_game_data_list:
    name = "shape" + str(i).zfill(4)
    init_object_file = open(os.path.join(out_path, name + "_init_object.json"), "w")
    init_object_file.write(pretty_pickle_json(item[0]))
    init_object_file.close()
    
    if item[1] is not None:
      shape_file = open(os.path.join(out_path, name + "_shape.json"), "w")
      shape_file.write(pretty_pickle_json(item[1]))
      shape_file.close()
    
    if item[2] is not None:
      gamedata_file = open(os.path.join(out_path, name + "_gamedata.json"), "w")
      gamedata_file.write(item[2].to_json())
      gamedata_file.close()

    i += 1
  
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

  def to_bytes(self):
    raw = struct.pack(float_endian, self.x)
    raw += struct.pack(float_endian, self.y)
    raw += struct.pack(float_endian, self.z)
    return raw
    

class Mesh:
  def __init__(self, mesh_offset, lightmap_offsets, lightmap_motifs, flags, cull_distance, tint, color_stream_count, color_stream_offset, init_offset):
    #get name from offset
    self.mesh_offset = mesh_offset
    current_offset = writer.tell()
    writer.seek(mesh_offset + init_offset)
    self.mesh_name = ''.join(iter(lambda: writer.read(1).decode('ascii'), '\x00')) #remove trailing zeroes

    self.lightmap_names = []
    self.lightmap_offsets = lightmap_offsets
    for item in lightmap_offsets:
      if int(item) > 0:
        writer.seek(item + init_offset)
        self.lightmap_names.append(''.join(iter(lambda: writer.read(1).decode('ascii'), '\x00'))) #remove trailing zeroes

    
    self.lightmap_motifs = lightmap_motifs
    self.flags = flags
    self.cull_distance = cull_distance
    self.tint = tint
    self.color_stream_count = color_stream_count
    self.color_stream_offset = color_stream_offset
    #reset the writer
    writer.seek(mesh_offset + init_offset)

  
  def print_data(self):
    print("Mesh Offset: " + str(self.mesh_offset))
    print("Mesh Name: " + str(self.mesh_name))
    print("Lightmap offsets: " + str(self.lightmap_offsets))
    print("Lightmap names: " + str(self.lightmap_names))
    print("Lightmap Motifs: " + str(self.lightmap_motifs))
    print("Flags: " + str(self.flags))
    print("Cull Distance: " + str(self.cull_distance))
    print("Tint: " + str(self.tint.print_data()))
    print("Color Stream Count: " + str(self.color_stream_count))
    print("Color Streams: " + str(self.color_stream_offset))

  def to_bytes(self, string_dict, lightmap_dict, init_relative_offset):
    # update mesh offset
    if self.mesh_name in string_dict: # If this mesh name already exists link to it
      self.mesh_offset = string_dict[self.mesh_name]
    else:
      #add init size to offset because string is right after
      self.mesh_offset = init_relative_offset + len(self.lightmap_offsets) * 6 + 32 
    
    for i in range(4):
      if len(self.lightmap_names) > i and len(self.lightmap_names[i]) > 0:
        if self.lightmap_names[i] in lightmap_dict:
          self.lightmap_offsets[i] = lightmap_dict[self.lightmap_names[i]]
        else:
          lightmap_dict[self.lightmap_names[i]] = self.lightmap_offsets[i]
      else:
        self.lightmap_offsets[i] = 0

    raw = struct.pack(int_endian, self.mesh_offset)
    for i in self.lightmap_offsets:
      raw += struct.pack(int_endian, i)
    for i in self.lightmap_motifs:
      raw += struct.pack(short_endian, i)
    raw += struct.pack(int_endian, self.flags)
    raw += struct.pack(float_endian, self.cull_distance)
    raw += self.tint.to_bytes()
    raw += struct.pack(int_endian, self.color_stream_count)
    raw += struct.pack(int_endian, self.color_stream_offset)
    #append the mesh name if it doesnt exist yet
    if self.mesh_name not in string_dict:
      string_dict[self.mesh_name] = self.mesh_offset
      new_bytes = bytearray(self.mesh_name.encode('ascii'))
      #add a null byte
      new_bytes.append(0x0)
      raw += new_bytes
    return raw

class Header:
  #Dictionary where key is name and value is value
  def __init__(self, writer):
    self.data = self.header_parse(writer)

  def header_parse(self, writer): 
    header = {}
    header['file_size'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    header['mesh_count'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False) #maybe meshes or something
    header['offset_to_mesh_inits'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    header['offset_to_mesh_sizes'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    header['size_of_mesh_part'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    header['offset_to_world'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    header['size_of_world'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    header['offset_to_streaming_data'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    header['size_of_streaming_data'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    header['offset_of_inits'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    header['size_of_inits'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    return header

  def print_header(self):
    print("--------------- World Header ---------------")
    for item in self.data:
      print(item + " : " + str(self.data[item]))
 
class InitHeader:
  #dictionary where key is name and value is value
  def __init__(self, writer, init_offset):
    self.data = self.header_parse(writer, init_offset)

  def header_parse(self, writer, init_offset): 
    header = {}
    writer.seek(init_offset)
    header['item_count'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    header['empty1'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    header['empty2'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    header['empty3'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    return header

  def print_header(self):
    print("--------------- Init Header ---------------")
    for item in self.data:
      print(item + " : " + str(self.data[item]))

  def to_bytes(self):
    byteheader = struct.pack(int_endian, self.data['item_count'])
    byteheader += struct.pack(int_endian, self.data['empty1'])
    byteheader += struct.pack(int_endian, self.data['empty2'])
    byteheader += struct.pack(int_endian, self.data['empty3'])
    return byteheader
    

class InitObject:
  #dictionary where key is name and value is value
  def __init__(self, writer, init_offset):
    self.data = self.init_parse(writer, init_offset)

  def init_parse(self, writer, init_offset): 
    header = {}
    header['offset'] = writer.tell()
    header['shape_type'] = shape_list[int.from_bytes(writer.read(4), byteorder=endian, signed=False)]
    header['shape_offset'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    header['orientation_of_shape1'] = struct.unpack(float_endian, writer.read(4))[0]
    header['orientation_of_shape2'] = struct.unpack(float_endian, writer.read(4))[0]
    header['orientation_of_shape3'] = struct.unpack(float_endian, writer.read(4))[0]
    header['orientation_of_shape4'] = struct.unpack(float_endian, writer.read(4))[0]
    header['orientation_of_shape5'] = struct.unpack(float_endian, writer.read(4))[0]
    header['orientation_of_shape6'] = struct.unpack(float_endian, writer.read(4))[0]
    header['orientation_of_shape7'] = struct.unpack(float_endian, writer.read(4))[0]
    header['orientation_of_shape8'] = struct.unpack(float_endian, writer.read(4))[0]
    header['orientation_of_shape9'] = struct.unpack(float_endian, writer.read(4))[0]
    header['orientation_of_shape10'] = struct.unpack(float_endian, writer.read(4))[0]
    header['orientation_of_shape11'] = struct.unpack(float_endian, writer.read(4))[0]
    header['orientation_of_shape12'] = struct.unpack(float_endian, writer.read(4))[0]
    header['shape_index'] = int.from_bytes(writer.read(4), byteorder=endian, signed=True)
    header['pointer_to_game_data'] = int.from_bytes(writer.read(4), byteorder=endian, signed=True)
    return header

  def print_init(self):
    print("--------------- Init Object ---------------")
    for item in self.data:
      print(item + " : "  + str(self.data[item]))

  def to_bytes(self):
    byteheader = struct.pack(int_endian, shape_value[self.data['shape_type']])
    byteheader += struct.pack(int_endian, self.data['shape_offset'])
    byteheader += struct.pack(float_endian, self.data['orientation_of_shape1'])
    byteheader += struct.pack(float_endian, self.data['orientation_of_shape2'])
    byteheader += struct.pack(float_endian, self.data['orientation_of_shape3'])
    byteheader += struct.pack(float_endian, self.data['orientation_of_shape4'])
    byteheader += struct.pack(float_endian, self.data['orientation_of_shape5'])
    byteheader += struct.pack(float_endian, self.data['orientation_of_shape6'])
    byteheader += struct.pack(float_endian, self.data['orientation_of_shape7'])
    byteheader += struct.pack(float_endian, self.data['orientation_of_shape8'])
    byteheader += struct.pack(float_endian, self.data['orientation_of_shape9'])
    byteheader += struct.pack(float_endian, self.data['orientation_of_shape10'])
    byteheader += struct.pack(float_endian, self.data['orientation_of_shape11'])
    byteheader += struct.pack(float_endian, self.data['orientation_of_shape12'])
    byteheader += struct.pack(int_endian, self.data['shape_index'])
    byteheader += struct.pack(int_endian, self.data['pointer_to_game_data'])
    return byteheader
    
class ShapeData:
  def __init__(self, writer, data_offset, shape_type, init_offset):
    self.shape_type = shape_type
    self.data = self.parse(writer, data_offset, init_offset)
    
  def parse(self, writer, data_offset, init_offset): 
    writer.seek(data_offset)
    #calculate bytes to read - different shapes are different sizes
    data = {}
    data['offset'] = data_offset
    if self.shape_type == "FWORLD_SHAPETYPE_POINT":
      None #no data for points
    elif self.shape_type == "FWORLD_SHAPETYPE_LINE":
      data['length'] = struct.unpack(float_endian, writer.read(4))[0] #single float length
    elif self.shape_type == "FWORLD_SHAPETYPE_SPLINE":
      data['point_count'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
      data['closed_spline'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False) #bool to or to not connect the first and last points
      data['vec_list_ptr'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
      vec_list = []
      #TODO FOLLOW THE POINTER TO SEE WHERE THIS ACTUALLY IS
      for i in range(data['point_count']):
        x = struct.unpack(float_endian, writer.read(4))[0]
        y = struct.unpack(float_endian, writer.read(4))[0]
        z = struct.unpack(float_endian, writer.read(4))[0]
        vec_list.append(Vector(3,x,y,z))
      data['array_of_points'] = vec_list #Massive array of points
    elif self.shape_type == "FWORLD_SHAPETYPE_BOX":
      #Box has 3 floats, x y z
      data['x'] = struct.unpack(float_endian, writer.read(4))[0] #X length
      data['y'] = struct.unpack(float_endian, writer.read(4))[0] #Y Length
      data['z'] = struct.unpack(float_endian, writer.read(4))[0] #Z Length
    elif self.shape_type == "FWORLD_SHAPETYPE_SPHERE":
      data['radius'] = struct.unpack(float_endian, writer.read(4))[0] #single float radius
    elif self.shape_type == "FWORLD_SHAPETYPE_CYLINDER":
      data['radius'] = struct.unpack(float_endian, writer.read(4))[0] #Radius
      data['y'] = struct.unpack(float_endian, writer.read(4))[0] #Y Length
    elif self.shape_type == "FWORLD_SHAPETYPE_MESH":
      name_offset = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
      lightmap_name_offsets = []
      lightmap_name_offsets.append(int.from_bytes(writer.read(4), byteorder=endian, signed=False))
      lightmap_name_offsets.append(int.from_bytes(writer.read(4), byteorder=endian, signed=False))
      lightmap_name_offsets.append(int.from_bytes(writer.read(4), byteorder=endian, signed=False))
      lightmap_name_offsets.append(int.from_bytes(writer.read(4), byteorder=endian, signed=False))
      lightmap_motifs = []
      lightmap_motifs.append(int.from_bytes(writer.read(2), byteorder=endian, signed=False))
      lightmap_motifs.append(int.from_bytes(writer.read(2), byteorder=endian, signed=False))
      lightmap_motifs.append(int.from_bytes(writer.read(2), byteorder=endian, signed=False))
      lightmap_motifs.append(int.from_bytes(writer.read(2), byteorder=endian, signed=False))
      flags = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
      cull_distance = struct.unpack(float_endian, writer.read(4))[0]
      color_x = struct.unpack(float_endian, writer.read(4))[0]
      color_y = struct.unpack(float_endian, writer.read(4))[0]
      color_z = struct.unpack(float_endian, writer.read(4))[0]
      tint = Vector(3,color_x,color_y,color_z)
      color_stream_count = int.from_bytes(writer.read(1), byteorder=endian, signed=False)
      writer.read(3) #only blank data here for alignment
      color_stream_offset = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
      data['mesh'] = Mesh(name_offset, lightmap_name_offsets, lightmap_motifs, flags, cull_distance, tint, color_stream_count, color_stream_offset, init_offset)
    elif self.shape_type == "FWORLD_SHAPETYPE_COUNT":
      None #Probably has no data
    return data

  def pretty_print(self):
    print("--------------- Shape Object ---------------")
    print("Offset:", self.data['offset'])
    print(self.shape_type)
    if self.shape_type == "FWORLD_SHAPETYPE_MESH":
      self.data['mesh'].print_data()
    else:
      for item in self.data:
        print(item + " : "  + str(self.data[item]))

  def to_bytes(self, string_dict, lightmap_dict, init_relative_offset):
    if self.shape_type == "FWORLD_SHAPETYPE_POINT":
      byteheader = None
    elif self.shape_type == "FWORLD_SHAPETYPE_LINE":
      byteheader = struct.pack(float_endian, self.data['length'])
    elif self.shape_type == "FWORLD_SHAPETYPE_SPLINE":
      byteheader = struct.pack(int_endian, self.data['point_count'])
      byteheader += struct.pack(int_endian, self.data['closed_spline'])
      self.data['vec_list_ptr'] = init_relative_offset + 12 #update pointer to new actual location
      byteheader += struct.pack(int_endian, self.data['vec_list_ptr']) #todo point to the proper data
      for i in self.data['array_of_points']:
        byteheader += i.to_bytes()
    elif self.shape_type == "FWORLD_SHAPETYPE_BOX":
      byteheader = struct.pack(float_endian, self.data['x'])
      byteheader += struct.pack(float_endian, self.data['y'])
      byteheader += struct.pack(float_endian, self.data['z'])
    elif self.shape_type == "FWORLD_SHAPETYPE_SPHERE":
      byteheader = struct.pack(float_endian, self.data['radius'])
    elif self.shape_type == "FWORLD_SHAPETYPE_CYLINDER":
      byteheader = struct.pack(float_endian, self.data['radius'])
      byteheader += struct.pack(float_endian, self.data['y'])
    elif self.shape_type == "FWORLD_SHAPETYPE_MESH":
      byteheader = self.data['mesh'].to_bytes(string_dict, lightmap_dict, init_relative_offset)
    elif self.shape_type == "FWORLD_SHAPETYPE_COUNT":
      byteheader = None
    return byteheader

class GameDataHeader:
  #dictionary where key is name and value is value
  def __init__(self, writer, data_offset):
    self.data = self.parse(writer, data_offset)
    self.tables = self.parse_tables(writer)

  def parse(self, writer, data_offset): 
    header = {}
    writer.seek(data_offset)
    header['offset'] = writer.tell()
    header['size'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    header['number_of_tables'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    header['pointer_to_tables'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    header['flags'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    return header
  
  def parse_tables(self,writer):
    tables = []
    offset = self.data['offset'] + self.data['pointer_to_tables']
    for i in range(self.data['number_of_tables']):
      tables.append(GameDataTable(writer, offset, self.data['offset']))
      offset += 16
    return tables

  def print_data(self):
    print("--------------- Game Data Header ---------------")
    for item in self.data:
      print(item + " : " + str(self.data[item]))

  def pretty_print(self):
    self.print_data()
    #print csv
    print("--------------- Game Data CSV ---------------")
    for item in self.tables:
      row = str(item.data['keystring'])
      row +=  " - " + str(item.data['keystring_length'])
      row += ","
      for field in item.fields:
        row += str(field.data_string())
        row += ","
      print(row)

  def size(self):
    size = 16 #header bytes
    for table in self.tables:
      size += table.size()
    return size;

  def to_bytes(self, init_relative_offset):
    #returns a byte array that can be lopped in with the other csv's
    #byteheader = struct.pack(int_endian, 0x3c23e147) #seems to be some special csv header magic number - SEEMS FALSE AS FUCK
    byteheader = struct.pack(int_endian, self.size())
    byteheader += struct.pack(int_endian, len(self.tables))
    byteheader += struct.pack(int_endian, 16) #size of the header, i think its always 16
    byteheader += struct.pack(int_endian, self.data['flags'])
    offset = (len(self.tables) * 16) + 16 #keystring headers are 16 bytes
    table_offset = offset #used to find the offset of the data part within a table's fields
    self.data['pointer_to_tables'] = len(byteheader)
    for table in self.tables:
      newheader = table.header_to_bytes(offset)
      byteheader += newheader
      offset += table.size() - 16 #-16 because the current header's count is already counted i guess #TODO check this
    #after headers you start pasting in values - not sure where the strings are kept yet
    for table in self.tables:
      #add keystrings
      table.data['keystring_pointer'] = len(byteheader)
      newbytes, size = table.keystring_to_bytes()
      byteheader += newbytes
      table_offset += size + len(table.fields) * 12 #data(strings) come after the keystring + fields
      table.data['field_offset'] = len(byteheader)
      #add fields
      for field in table.fields:
        new_bytes = field.to_bytes(table_offset)
        if field.data['string_length'] > 0:
          table_offset += field.data['string_length'] + 1 #add extra ending null byte!
        byteheader += new_bytes
        field.data['string_pointer'] = len(byteheader)
      #add field strings
      for field in table.fields:
        if field.data['data_type'] == "STRING":
          new_bytes = bytearray(field.data['string'])
          new_bytes.append(0x0)
          byteheader += new_bytes
        elif field.data['data_type'] == "WIDESTRING":
          new_bytes = bytearray(field.data['widestring'])
          new_bytes.append(0x0)
          byteheader += new_bytes   
    return byteheader

  def to_json(self):
    json_dict = self.data
    for item in self.tables:
      fields_list = []
      for field in item.fields:
        if field.data['data_type'] == "STRING":
          fields_list.append(field.data['string'].decode('ascii'))
        elif field.data['data_type'] == "WIDESTRING":
          fields_list.append(field.data['widestring'].decode('utf-16-le'))
        else:
          fields_list.append(field.data['float'])
      # keys are non unique so have to ad an identifier that i can remove later  
      new_keystring = item.data['keystring'].decode()
      i=1
      while new_keystring in json_dict:
        new_keystring = item.data['keystring'].decode() + "__" + str(i)
        i += 1
      json_dict[new_keystring] = fields_list
    return pretty_json(json.dumps(json_dict))
  
  def from_json(self, json_str):
    json_dict = json.loads(json_str)
    self.data = {}
    self.tables = []
    for key, value in json_dict.items():
      if key == "offset":
        self.data["offset"] = value #TODO set to 0 for memes?
      elif key == "size":
        self.data["size"] = value
      elif key == "number_of_tables":
        self.data["number_of_tables"] = value
      elif key == "pointer_to_tables":
        self.data["pointer_to_tables"] = value #TODO set to 0 for memes?
      elif key == "flags":
        self.data["flags"] = value
      else:
        #key is keystring, values is tables
        datatable = Empty()
        datatable.__class__ = GameDataTable
        datatable.data = {}
        datatable.data['offset'] = 0
        datatable.data['header_offset'] = 0
        datatable.data['keystring_pointer'] = 0
        #remove added text added to nonunique keystrings
        keystring =key.split("__")[0]
        datatable.data['keystring'] = keystring.encode('ascii')
        datatable.data['keystring_length'] = len(keystring)
        datatable.data['num_fields'] = len(value)
        datatable.data['table_index'] = len(self.tables)
        datatable.data['field_offset'] = 0

        fields = []
        for i in value:
          field = Empty()
          field.__class__ = GameDataField
          field.data = {}
          field.data['offset'] = 0
          if type(i) == float or type(i) == int: # if float
            field.data['data_type'] = "FLOAT"
            field.data['float'] = float(i)
            field.data['string_length'] = 0
            field.data['string_pointer'] = 0
          else:
            #Never seen case of widestring used
            field.data['data_type'] = "STRING"
            field.data['string_pointer'] = 0
            field.data['string'] = i.encode('ascii')
            field.data['string_length'] = len(i)
          fields.append(field)
        datatable.fields = fields
        self.tables.append(datatable)
    self.data["number_of_tables"] = len(self.tables)      

class GameDataTable:
  def __init__(self, writer, data_offset, header_offset):
    self.data = self.parse(writer, data_offset, header_offset)
    self.fields = self.parse_fields(writer, header_offset)

  def parse(self, writer, data_offset, header_offset): 
    table = {}
    writer.seek(data_offset)
    table['offset'] = writer.tell()
    table['header_offset'] = header_offset
    table['keystring_pointer'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    table['keystring_length'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    table['num_fields'] = int.from_bytes(writer.read(2), byteorder=endian, signed=False)
    table['table_index'] = int.from_bytes(writer.read(2), byteorder=endian, signed=False)
    table['field_offset'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    #Keystring
    writer.seek(header_offset + table['keystring_pointer'])
    table['keystring'] = writer.read(table['keystring_length'])
    return table
  
  def parse_fields(self, writer, header_offset):
    #save old offset to return
    original_offset = writer.tell()
    fields = []
    writer.seek(self.data['header_offset'] + self.data['field_offset'])
    for i in range(self.data['num_fields']):
      fields.append(GameDataField(writer, header_offset))
    writer.seek(original_offset)
    return fields;

  def print_data(self):
    print("--------------- Game Data Table ---------------")
    for item in self.data:
      print(item + " : " + str(self.data[item]))
    for item in self.fields:
      item.print_data()
  
  def size(self):
    size = 16 #header
    size += roundup_4(self.data['keystring_pointer'] + self.data['keystring_length'] + 1) - (self.data['keystring_pointer']); 
    #keystring does appears to add 1 null byte that is rounded to nearest int and then a null int after
    size += self.child_size()
    return size;
  
  def child_size(self):
    size = 0
    for field in self.fields:
      size += field.size()
    return size;
    

  def header_to_bytes(self, keystring_pointer):
    byteheader = struct.pack(int_endian, keystring_pointer) #parent has to figure out where it goes because its managing the rebuild
    byteheader += struct.pack(int_endian, len(self.data['keystring']))
    byteheader += struct.pack(short_endian, self.data['num_fields'])
    byteheader += struct.pack(short_endian, self.data['table_index'])
    byteheader += struct.pack(int_endian, self.data['field_offset'])
    return byteheader

  def keystring_to_bytes(self):
    keystring = bytearray(self.data['keystring'])
    #add additional padding to the string
    size = roundup_4(self.data['keystring_pointer'] + self.data['keystring_length'] + 1) - (self.data['keystring_pointer']); 
    to_add = size - len(keystring)
    for i in range(to_add):
      keystring.append(0x0)
     
    byteheader = keystring
    return byteheader, size
    

class GameDataField:
  def __init__(self, writer, header_offset):
    self.data = self.parse(writer, header_offset)

  def parse(self, writer, header_offset): 
    entry = {}
    entry['offset'] = writer.tell()
    entry['data_type'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    if entry['data_type'] > 3:
      entry['data_type'] = "FLOAT"
    else: 
      entry['data_type'] = csv_datatype[entry['data_type']]
    if entry['data_type'] == "STRING":
      entry['string_pointer'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    elif entry['data_type'] == "WIDESTRING":
      entry['widestring_pointer'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    else:
      entry['float'] = struct.unpack(float_endian, writer.read(4))[0]
    entry['string_length'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)

    #add string and dont forget to reset writer
    if entry['data_type'] == "STRING":
      old_offset = writer.tell()
      writer.seek(header_offset + entry['string_pointer'])
      entry['string'] = writer.read(entry['string_length'])
      writer.seek(old_offset)
    elif entry['data_type'] == "WIDESTRING": 
      old_offset = writer.tell()
      writer.seek(header_offset + entry['widestring_pointer'])
      entry['widestring'] = writer.read(entry['string_length'])
      writer.seek(old_offset)
    return entry
  
  def print_data(self):
    print("--------------- Game Data Entry ---------------")
    for item in self.data:
      print(item + " : " + str(self.data[item]))
  
  def data_string(self):
    if self.data['data_type'] == "STRING":
      return self.data['string'].decode('ascii')
    elif self.data['data_type'] == "WIDESTRING":
      return self.data['widestring'].decode('utf-16-le')
    else:
      return self.data['float']
  
  def size(self):
    size = 12 #header size
    #if data is a string, dont forget to add 4 bytes for the offset
    if self.data['data_type'] == "STRING" or self.data['data_type'] == "WIDESTRING":
      size += 1
      size += self.data['string_length'] #this string does not appear to be rounded up
    return size;
  
  def to_bytes(self, offset):
    byteheader = struct.pack(int_endian, csv_datavalue[self.data['data_type']])
    #data - either a pointer or a float
    if self.data['data_type'] == "STRING" or self.data['data_type'] == "WIDESTRING":
      byteheader += struct.pack(int_endian, offset) #parent has to figure out where it goes because its managing the rebuild
    else:
      byteheader += struct.pack(float_endian, self.data['float']) #no string, no offset
    #string length
    if self.data['data_type'] == "STRING" or self.data['data_type'] == "WIDESTRING":
      byteheader += struct.pack(int_endian, self.data['string_length'])
    else: 
      byteheader += struct.pack(int_endian, 0) #no string, no offset
    return byteheader
    

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Extract or rebuild a wld file")
  endian = parser.add_mutually_exclusive_group()
  endian.add_argument("-g", "--gamecube", help="Use gamecube endian - big endian", action="store_true")
  endian.add_argument("-x", "--xbox", help="Use xbox endian - big endian [Default]", action="store_true")
  operation = parser.add_mutually_exclusive_group()
  operation.add_argument("-e", "--extract", help="Extract the contents of a wld file to a directory", action="store_true")
  operation.add_argument("-r", "--rebuild", help="Rebuild a wld file from a folder full of extracted files", action="store_true")
  parser.add_argument("-p", "--print", help="Print the structures to stdout", action="store_true")
  parser.add_argument("input", help="input file or folder")
  parser.add_argument("output", help="output file or folder")
  args = parser.parse_args()

  #set endianess - xbox default
  if args.gamecube:
    endian='big'
    float_endian = '>f'
    int_endian = '>i'
    short_endian = '>h' 
  else:
    endian='little'
    float_endian = '<f'
    int_endian = '<i'
    short_endian = '<h' 

  #get input
  if args.extract:
    path = args.input
    writer = open(path, "rb")
    header, initHeader, init_shape_game_data_list = parse_wld_file(writer)
  elif args.rebuild:
    preinit, header, initHeader, init_shape_game_data_list = import_from_folder(args.input)
  else:
    print("Must specify extract or rebuild")
    sys.exit()
    

  #print
  if args.print:
    print_classes(header, initHeader, init_shape_game_data_list)
    
  
  if args.extract:
    extract_to_file(writer, args.output, header, initHeader, init_shape_game_data_list)
  elif args.rebuild:
    lightmap_name_locations_dict = {}
    #ALWAYS RUN THIS TWICE SO YOU CAN UPDATE OFFSETS
    build_wld_file(args.output, preinit, initHeader, init_shape_game_data_list, header.data['offset_of_inits'] + 16, lightmap_name_locations_dict)
    build_wld_file(args.output, preinit, initHeader, init_shape_game_data_list, header.data['offset_of_inits'] + 16, lightmap_name_locations_dict)
  

  
