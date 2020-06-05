import sys
import os
import shutil
import struct
import math
import json
import jsonpickle
import argparse

#set of ma specific classes
from lib import ma_util, init_classes#, mesh_classes

#Notes - generates an outfile twice so it can easily fix offsets without having to keep track of where things are

endian='little'
float_endian = '<f'
int_endian = '<i'
short_endian = '<h'

fpath=os.path.realpath(__file__)
py_path=os.path.dirname(fpath)

def parse_wld_file(writer):

  header = init_classes.Header(writer)

  #meshHeader = mesh_classes.MeshHeader(writer, header.data['offset_to_mesh_inits'])
  meshHeader = None
  
  #mesh_size_list = []
  #writer.seek(header.data['offset_to_mesh_sizes'])
  #for item in range(header.data['mesh_count']):
  #  mesh_size_list.append(int.from_bytes(writer.read(4), byteorder=endian, signed=False))
  #
  #print (sum( mesh_size_list))

  mesh_list = []
  #offset = meshHeader.data['offset_to_mesh_table']
  #for i in range(header.data['mesh_count']):
  #  writer.seek(offset)
  #  mesh_list.append(mesh_classes.MeshObject(writer, mesh_size_list[i]))
  #  #add current mesh's size to offset
  #  offset = ma_util.roundup(offset + mesh_size_list[i])
  
  initHeader = init_classes.InitHeader(writer,header.data['offset_of_inits'])

  init_object_list = []
  init_shape_game_data_list = [] #all the init entries and shapes and game datas refer to the same thing
  for item in range(initHeader.data['item_count']):
    init_object_list.append(init_classes.InitObject(writer,header.data['offset_of_inits']))

  for item in init_object_list:
    #add offset of init header table + size of init header
    offset = item.data['shape_offset'] + header.data['offset_of_inits'] + 16  #16 byte header
    shape = init_classes.ShapeData(writer,offset,item.data['shape_type'], header.data['offset_of_inits'] + 16)
    gamedata = None
    if item.data['pointer_to_game_data'] > 0:
      #add offset of init header table + size of init header
      offset = item.data['pointer_to_game_data'] + header.data['offset_of_inits'] + 16  #16 byte header
      gamedata = init_classes.GameDataHeader(writer,offset)
    init_shape_game_data_list.append([item, shape, gamedata])
  
  return header, meshHeader, mesh_list, initHeader, init_shape_game_data_list

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
      out_bytes += bytes(ma_util.roundup_4(len(out_bytes)) - len(out_bytes))
      #go back and update the shape index as to where you are
      init_relative_offset = len(out_bytes) - start_of_inits
      new_bytes = item[1].to_bytes(mesh_name_locations_dict, lightmap_name_locations_dict, init_relative_offset)
      if new_bytes is not None:
        item[0].data['shape_offset'] = init_relative_offset
        out_bytes += new_bytes
      #always align
      out_bytes += bytes(ma_util.roundup_4(len(out_bytes)) - len(out_bytes))
    else:
      #go back and update the shape index as to where you are
      init_relative_offset = len(out_bytes) - start_of_inits
      new_bytes = item[1].to_bytes(mesh_name_locations_dict, lightmap_name_locations_dict, init_relative_offset)
      if new_bytes is not None:
        item[0].data['shape_offset'] = init_relative_offset
        out_bytes += new_bytes
      #always align
      out_bytes += bytes(ma_util.roundup_4(len(out_bytes)) - len(out_bytes))
      if item[2] is not None:
        #go back and update the shape index as to where you are
        init_relative_offset = len(out_bytes) - start_of_inits
        item[0].data['pointer_to_game_data'] = init_relative_offset
        out_bytes += item[2].to_bytes(init_relative_offset)
      #make sure to align
      out_bytes += bytes(ma_util.roundup_4(len(out_bytes)) - len(out_bytes))

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

def import_from_folder(directory): 
  return ma_util.wld_folder_to_init_shape_gamedata(directory)

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
  header_file.write(ma_util.pretty_pickle_json(header))
  header_file.close()

  init_header_file = open(os.path.join(out_path, "init_header.json"), "w")
  init_header_file.write(ma_util.pretty_pickle_json(init_header))
  init_header_file.close()

  i = 0
  used_name_list=[]
  for item in init_shape_game_data_list:
    if item[2] is not None:
      itemname = ""
      itemtype = ""
      for table in item[2].tables:
        keystring = table.data['keystring'].decode()
        if keystring.lower() == "name":
          itemname = table.fields[0].data_string()
        elif keystring.lower() == "type":
          itemtype = table.fields[0].data_string()
      basename = ""
      if itemtype:
        basename+=itemtype
      else:
        basename+="shape"
      basename += '-'
      if itemname:
        basename+=itemname
      else:
        basename+="unnamed"
      basename += '-'

      basename = ''.join(x.capitalize() or '_' for x in basename.split('_'))
      j=0
      while basename+str(j).zfill(4) in used_name_list:
        j+=1
      name = basename+str(j).zfill(4)
      used_name_list.append(name)
    else:
      name = "shape" + str(i).zfill(4)
    init_object_file = open(os.path.join(out_path, name + "_init_object.json"), "w")
    init_object_file.write(ma_util.pretty_pickle_json(item[0]))
    init_object_file.close()
    
    if item[1] is not None:
      shape_file = open(os.path.join(out_path, name + "_shape.json"), "w")
      shape_file.write(ma_util.pretty_pickle_json(item[1]))
      shape_file.close()
    
    if item[2] is not None:
      gamedata_file = open(os.path.join(out_path, name + "_gamedata.json"), "w")
      gamedata_file.write(item[2].to_json())
      gamedata_file.close()

    i+=1

def print_classes(header, meshHeader, mesh_list, initHeader, init_shape_game_data_list):
  header.print_header()
  initHeader.print_header()

def execute(is_big_endian, extract, rebuild, insert, print_data, input, output):
  global endian
  global float_endian
  global int_endian
  global short_endian
  #set endianess - xbox default
  if is_big_endian:
    endian='big'
    float_endian = '>f'
    int_endian = '>i'
    short_endian = '>h' 
    init_classes.endian='big'
    init_classes.float_endian = '>f'
    init_classes.int_endian = '>i'
    init_classes.short_endian = '>h' 
  else:
    endian='little'
    float_endian = '<f'
    int_endian = '<i'
    short_endian = '<h' 
    init_classes.endian='little'
    init_classes.float_endian = '<f'
    init_classes.int_endian = '<i'
    init_classes.short_endian = '<h' 
  #get input
  if extract or insert:
    path = input
    writer = open(path, "rb")
    header, meshHeader, mesh_list, initHeader, init_shape_game_data_list = parse_wld_file(writer)
  elif rebuild:
    preinit, header, initHeader, init_shape_game_data_list = import_from_folder(input)
  else:
    print("Must specify extract or rebuild or insert")
    sys.exit()
  
  if insert:
    #replace shapes
    _,_,_, init_shape_game_data_list = import_from_folder(output)
    #get preinit
    writer.seek(0)
    preinit = bytearray(writer.read(header.data['offset_of_inits']))
    #update initheader
    initHeader.data['item_count'] = len(init_shape_game_data_list)
    #output to the same file you read in from
    output = input

  meshHeader=""
  mesh_list=[]
  if print_data:
    print_classes(header, meshHeader, mesh_list, initHeader, init_shape_game_data_list)
    
  if extract:
    extract_to_file(writer, output, header, initHeader, init_shape_game_data_list)
  elif rebuild or insert:
    lightmap_name_locations_dict = {}
    #ALWAYS RUN THIS TWICE SO YOU CAN UPDATE OFFSETS
    build_wld_file(output, preinit, initHeader, init_shape_game_data_list, header.data['offset_of_inits'] + 16, lightmap_name_locations_dict)
    build_wld_file(output, preinit, initHeader, init_shape_game_data_list, header.data['offset_of_inits'] + 16, lightmap_name_locations_dict)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Extract or rebuild a wld file")
  parser_endian = parser.add_mutually_exclusive_group()
  parser_endian.add_argument("-g", "--gamecube", help="Use gamecube endian - small endian", action="store_true")
  parser_endian.add_argument("-x", "--xbox", help="Use xbox endian - big endian [Default]", action="store_true")
  operation = parser.add_mutually_exclusive_group()
  operation.add_argument("-e", "--extract", help="Extract the contents of a wld file to a directory", action="store_true")
  operation.add_argument("-r", "--rebuild", help="Rebuild a wld file from a folder full of extracted files", action="store_true")
  operation.add_argument("-i", "--insert", help="Inserts a folder full of shapes into the wld, overwriting the current shapes, put the .wld file as input and a folder containing shapes as output", action="store_true")
  parser.add_argument("-p", "--print", help="Print the structures to stdout", action="store_true")
  parser.add_argument("input", help="input file or folder")
  parser.add_argument("output", help="output file or folder")
  args = parser.parse_args()

  execute(args.gamecube, args.extract, args.rebuild, args.insert, args.print, args.input, args.output)
  

  
