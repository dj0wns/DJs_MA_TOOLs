import struct
import os
import sys
import json

from . import ma_util

#globals because i dont want to rewrite this - make sure to set them to the correct value - xbox default
endian='little'
float_endian = '<f'
int_endian = '<i'
short_endian = '<h'

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
  
class Mesh:
  def __init__(self, mesh_offset, lightmap_offsets, lightmap_motifs, flags, cull_distance, tint, color_stream_count, color_stream_offset, init_offset, writer):
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
    raw += self.tint.to_bytes(float_endian)
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
    header['Right_X'] = struct.unpack(float_endian, writer.read(4))[0]
    header['Right_Y'] = struct.unpack(float_endian, writer.read(4))[0]
    header['Right_Z'] = struct.unpack(float_endian, writer.read(4))[0]
    header['Up_X'] = struct.unpack(float_endian, writer.read(4))[0]
    header['Up_Y'] = struct.unpack(float_endian, writer.read(4))[0]
    header['Up_Z'] = struct.unpack(float_endian, writer.read(4))[0]
    header['Front_X'] = struct.unpack(float_endian, writer.read(4))[0]
    header['Front_Y'] = struct.unpack(float_endian, writer.read(4))[0]
    header['Front_Z'] = struct.unpack(float_endian, writer.read(4))[0]
    header['Position_X'] = struct.unpack(float_endian, writer.read(4))[0]
    header['Position_Y'] = struct.unpack(float_endian, writer.read(4))[0]
    header['Position_Z'] = struct.unpack(float_endian, writer.read(4))[0]
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
    byteheader += struct.pack(float_endian, self.data['Right_X'])
    byteheader += struct.pack(float_endian, self.data['Right_Y'])
    byteheader += struct.pack(float_endian, self.data['Right_Z'])
    byteheader += struct.pack(float_endian, self.data['Up_X'])
    byteheader += struct.pack(float_endian, self.data['Up_Y'])
    byteheader += struct.pack(float_endian, self.data['Up_Z'])
    byteheader += struct.pack(float_endian, self.data['Front_X'])
    byteheader += struct.pack(float_endian, self.data['Front_Y'])
    byteheader += struct.pack(float_endian, self.data['Front_Z'])
    byteheader += struct.pack(float_endian, self.data['Position_X'])
    byteheader += struct.pack(float_endian, self.data['Position_Y'])
    byteheader += struct.pack(float_endian, self.data['Position_Z'])
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
        vec_list.append(ma_util.Vector(3,x,y,z))
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
      tint = ma_util.Vector(3,color_x,color_y,color_z)
      color_stream_count = int.from_bytes(writer.read(1), byteorder=endian, signed=False)
      writer.read(3) #only blank data here for alignment
      color_stream_offset = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
      data['mesh'] = Mesh(name_offset, lightmap_name_offsets, lightmap_motifs, flags, cull_distance, tint, color_stream_count, color_stream_offset, init_offset, writer)
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
        byteheader += i.to_bytes(float_endian)
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
    return ma_util.pretty_json(json.dumps(json_dict))
  
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
        datatable = ma_util.Empty()
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
          field = ma_util.Empty()
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
    size += ma_util.roundup_4(self.data['keystring_pointer'] + self.data['keystring_length'] + 1) - (self.data['keystring_pointer']); 
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
    size = ma_util.roundup_4(self.data['keystring_pointer'] + self.data['keystring_length'] + 1) - (self.data['keystring_pointer']); 
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
