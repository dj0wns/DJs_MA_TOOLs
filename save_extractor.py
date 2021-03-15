import sys
import os
import shutil
import struct
import math
import json
import jsonpickle
import argparse
import zlib

#set of ma specific classes
from lib import ma_util, save_classes

endian='little'
float_endian = '<f'
int_endian = '<i'
short_endian = '<h'

constant = 0x55501234

fpath=os.path.realpath(__file__)
py_path=os.path.dirname(fpath)

def parse_save_file(reader):
  while constant != int.from_bytes(reader.read(4), byteorder=endian, signed=False):
    None
  reader.seek(-4,1)
  profile_data = save_classes.ProfileData()
  profile_data.parse_bytes(reader)
  return profile_data

def build_save_file(path, profile_data):
  print(profile_data.data["header"].data['profile_crc'])
  reader = open(path, "rb")
  
  out_bytes = profile_data.to_bytes()

  writer = open(path + ".new", "wb")
  
  while True:
    test = int.from_bytes(reader.read(4), byteorder=endian, signed=False)
    if constant == test:
      break
    writer.write(struct.pack(int_endian, test))
  profile_offset = writer.tell()
  writer.write(out_bytes)
  end_offset = writer.tell()
  reader.seek(end_offset)

  end_data = reader.read()
  writer.write(end_data) #sandwich any excess data in case i missed anything
  reader.close()
  writer.close()
  
  #calculate new profile crc
  crc_reader = open(path + ".new", "rb")
  crc_reader.seek(profile_offset + profile_data.data["header"].size())
  crc_data = crc_reader.read(profile_data.size())
  profile_data.data["header"].data['profile_crc'] = zlib.crc32(crc_data)
  print(zlib.crc32(crc_data))

  if endian == 'little':
    #xbox bin
    None
  else:
    #also update the header endian
    crc_reader.seek(68)
    crc_data = crc_reader.read(31912)
    crc = zlib.crc32(crc_data)
    writer = open(path + ".new", "r+b")
    writer.seek(64)
    writer.write(struct.pack(int_endian, crc))
  
  crc_reader.close()





def extract_to_file(out_path, profile_data):
  profile_file = open(out_path, "w")
  profile_file.write(ma_util.pretty_pickle_json(profile_data))
  profile_file.close()

def import_from_file(in_path):
  data = open(in_path, "r").read()
  profile_data = jsonpickle.decode(data)
  return profile_data

def print_classes(profile_data):
  print("Size: " + str(profile_data.size()))
  profile_data.print_data()

def execute(is_big_endian, extract, rebuild, print_data, input, output):
  global endian
  global float_endian
  global int_endian
  global short_endian
  #set endianess - xbox default
  if is_big_endian:
    endian='big'
    float_endian = '>f'
    int_endian = '>I'
    short_endian = '>H' 
    save_classes.endian='big'
    save_classes.float_endian = '>f'
    save_classes.int_endian = '>I'
    save_classes.short_endian = '>H' 
  else:
    endian='little'
    float_endian = '<f'
    int_endian = '<I'
    short_endian = '<H' 
    save_classes.endian='little'
    save_classes.float_endian = '<f'
    save_classes.int_endian = '<I'
    save_classes.short_endian = '<H' 
  #get input
  if extract:
    path = input
    reader = open(path, "rb")
    profile_data = parse_save_file(reader)
  elif rebuild:
    profile_data = import_from_file(input)
  else:
    print("Must specify extract or rebuild or insert")
    sys.exit()
  
  if print_data:
    print_classes(profile_data)
    
  if extract:
    extract_to_file(output, profile_data)
  elif rebuild:
    #ALWAYS RUN THIS TWICE SO YOU CAN UPDATE OFFSETS
    build_save_file(output, profile_data)
    build_save_file(output, profile_data)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Extract or rebuild a profile save file")
  parser_endian = parser.add_mutually_exclusive_group()
  parser_endian.add_argument("-g", "--gamecube", help="Use gamecube endian - small endian - .gci", action="store_true")
  parser_endian.add_argument("-x", "--xbox", help="Use xbox endian - big endian [Default] - .bin", action="store_true")
  operation = parser.add_mutually_exclusive_group()
  operation.add_argument("-e", "--extract", help="Extract the contents of a profile to an old save file", action="store_true")
  operation.add_argument("-r", "--rebuild", help="Rebuild a profile save from an extracted file", action="store_true")
  parser.add_argument("-p", "--print", help="Print the structures to stdout", action="store_true")
  parser.add_argument("input", help="input file")
  parser.add_argument("output", help="output file")
  args = parser.parse_args()

  execute(args.gamecube, args.extract, args.rebuild, args.print, args.input, args.output)
  

  
