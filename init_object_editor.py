import sys
import os
import shutil
import struct
import math

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

def roundup(x):
  return int(math.ceil(x / 16.0)) * 16

def roundup_4(x):
  return int(math.ceil(x / 4.0)) * 4

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

    self.lightmap_offsets = lightmap_offsets
    
    #TODO get lightmap names from offsets
   # if lightmap_offsets > 0:
   #   writer.seek(mesh_offset + init_offset)
   #   self.lightmap_names = writer.read(12)
   # else:
    self.lightmap_names = "N/A"
    
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

  def to_bytes(self, string_dict):
    if self.mesh_name in string_dict: # If this mesh name already exists link to it
      raw = struct.pack(int_endian, string_dict[self.mesh_name])
    else:
      #TODO update to use actual position
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
      #TODO add the proper offset
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

  def to_bytes(self, string_dict):
    if self.shape_type == "FWORLD_SHAPETYPE_POINT":
      byteheader = None
    elif self.shape_type == "FWORLD_SHAPETYPE_LINE":
      byteheader = struct.pack(float_endian, self.data['length'])
    elif self.shape_type == "FWORLD_SHAPETYPE_SPLINE":
      byteheader = struct.pack(int_endian, self.data['point_count'])
      byteheader += struct.pack(int_endian, self.data['closed_spline'])
      byteheader += struct.pack(int_endian, self.data['vec_list_ptr']) #todo point to the proper data
      for i in self.data['array_of_points']:
        byteheader += i.to_bytes()
    elif self.shape_type == "FWORLD_SHAPETYPE_BOX":
      print("Moo")
      byteheader = struct.pack(float_endian, self.data['x'])
      byteheader += struct.pack(float_endian, self.data['y'])
      byteheader += struct.pack(float_endian, self.data['z'])
    elif self.shape_type == "FWORLD_SHAPETYPE_SPHERE":
      byteheader = struct.pack(float_endian, self.data['radius'])
    elif self.shape_type == "FWORLD_SHAPETYPE_CYLINDER":
      byteheader = struct.pack(float_endian, self.data['radius'])
      byteheader += struct.pack(float_endian, self.data['y'])
    elif self.shape_type == "FWORLD_SHAPETYPE_MESH":
      byteheader = self.data['mesh'].to_bytes(string_dict)
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

  def to_bytes(self):
    #returns a byte array that can be lopped in with the other csv's
    #byteheader = struct.pack(int_endian, 0x3c23e147) #seems to be some special csv header magic number - SEEMS FALSE AS FUCK
    byteheader = struct.pack(int_endian, self.size())
    byteheader += struct.pack(int_endian, len(self.tables))
    byteheader += struct.pack(int_endian, 16) #size of the header, i think its always 16
    byteheader += struct.pack(int_endian, self.data['flags'])
    offset = (len(self.tables) * 16) + 16 #keystring headers are 16 bytes
    table_offset = offset #used to find the offset of the data part within a table's fields
    for table in self.tables:
      newheader = table.header_to_bytes(offset)
      byteheader += newheader
      offset += table.size() - 16 #-16 because the current header's count is already counted i guess #TODO check this
    #after headers you start pasting in values - not sure where the strings are kept yet
    for table in self.tables:
      #add keystrings
      newbytes, size = table.keystring_to_bytes()
      byteheader += newbytes
      table_offset += size + len(table.fields) * 12 #data(strings) come after the keystring + fields
      #add fields
      for field in table.fields:
        new_bytes = field.to_bytes(table_offset)
        if field.data['string_length'] > 0:
          table_offset += field.data['string_length'] + 1 #add extra ending null byte!
        byteheader += new_bytes
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


class GameDataTable:
  def __init__(self, writer, data_offset, header_offset):
    self.data = self.parse(writer, data_offset, header_offset)
    self.fields = self.parse_fields(writer)

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
  
  def parse_fields(self, writer):
    #save old offset to return
    original_offset = writer.tell()
    fields = []
    writer.seek(self.data['header_offset'] + self.data['field_offset'])
    for i in range(self.data['num_fields']):
      fields.append(GameDataField(writer))
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
  def __init__(self, writer):
    self.data = self.parse(writer)

  def parse(self, writer): 
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
      writer.seek(offset + entry['string_pointer'])
      entry['string'] = writer.read(entry['string_length'])
      writer.seek(old_offset)
    elif entry['data_type'] == "WIDESTRING": 
      old_offset = writer.tell()
      writer.seek(entry['offset'] + entry['widestring_pointer'])
      entry['widestring'] = writer.read(entry['string_length'])
      writer.seek(old_offset)
    return entry
  
  def print_data(self):
    print("--------------- Game Data Entry ---------------")
    for item in self.data:
      print(item + " : " + str(self.data[item]))
  
  def data_string(self):
    if self.data['data_type'] == "STRING":
      return self.data['string'].decode()
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
  if len(sys.argv) < 2 : 
    print("Requires a world file as an argument.")
    sys.exit()

  path = sys.argv[1]
  writer = open(path, "rb")

  #extract name for creating a working folder
  basename = os.path.basename(path)
  filename, file_extension = os.path.splitext(basename)

  header = Header(writer)
  header.print_header()
  
  initHeader = InitHeader(writer,header.data['offset_of_inits'])
  initHeader.print_header()

  init_object_list = []
  shape_game_data_list = []
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
    shape_game_data_list.append([shape, gamedata])
    item.print_init()
  
  for item in shape_game_data_list:
    item[0].pretty_print()
    if item[1] is not None:
      item[1].pretty_print()
  print("num inits: " + str(len(init_object_list)))
  print("num shape objects: " + str(len(shape_game_data_list)))


  #rebuild the init section by copying everything else then adding new inits
  writer.seek(0)
  out_bytes = bytearray(writer.read(header.data['offset_of_inits']))
  
  out_bytes += initHeader.to_bytes()

  for item in init_object_list:
    out_bytes += item.to_bytes()
  
  mesh_name_locations_dict = {} #used so mesh name strings are only used once to match implementation
  
  for item in shape_game_data_list:
    #if its a mesh then data is before the shape other wise reverse it
    if item[0].shape_type == "FWORLD_SHAPETYPE_MESH":
      if item[1] is not None:
        out_bytes += item[1].to_bytes()
      #make sure to align
      out_bytes += bytes(roundup_4(len(out_bytes)) - len(out_bytes))
      new_bytes = item[0].to_bytes(mesh_name_locations_dict)
      if new_bytes is not None:
        out_bytes += new_bytes
      #always align
      out_bytes += bytes(roundup_4(len(out_bytes)) - len(out_bytes))
    else:
      new_bytes = item[0].to_bytes(mesh_name_locations_dict)
      if new_bytes is not None:
        out_bytes += new_bytes
      #always align
      out_bytes += bytes(roundup_4(len(out_bytes)) - len(out_bytes))
      if item[1] is not None:
        out_bytes += item[1].to_bytes()
      #make sure to align
      out_bytes += bytes(roundup_4(len(out_bytes)) - len(out_bytes))

  outfile = open(path+".temp", "wb")
  outfile.write(out_bytes)
