import sys
import os
import shutil
import re
import glob
import struct
import math
import collections
import argparse


fpath=os.path.realpath(__file__)
py_path=os.path.dirname(fpath)
endian = "little"
pack_int = '<i'
INT_BYTES=4
STR_BYTES=20

#A dirty file injector for msts

def roundup(x):
#  return int(math.ceil(x / 16.0)) * 16
  return x

def add_buffer(data):
  current_offset = len(data)
  buffer_to_add = roundup(current_offset) - current_offset
  for i in range(buffer_to_add):
    data.append(0)

def insert(mst_data, insert_file_name, insert_reader):
  mst_data_out = bytearray()
  #search for file entry in mst
  b = bytearray()
  b.extend(map(ord, insert_file_name))
  idx = mst_data.find(b)
  entry_location = idx

  #read table entry
  original_name = mst_data[idx:idx+STR_BYTES]
  idx+=STR_BYTES
  original_location = int.from_bytes(mst_data[idx:idx+INT_BYTES], endian)
  idx+=INT_BYTES
  original_length = int.from_bytes(mst_data[idx:idx+INT_BYTES], endian)
  idx+=INT_BYTES
  original_timestamp = int.from_bytes(mst_data[idx:idx+INT_BYTES], endian)
  idx+=INT_BYTES
  original_crc = int.from_bytes(mst_data[idx:idx+INT_BYTES], endian)
  idx+=INT_BYTES

  print("Seek: " + str(idx))
  print("Original File: " + str(bytes(original_name).decode()) + ", location: " + str(original_location) + ", length: " + str(original_length) + ", timestamp: " + str(original_timestamp) + ", crc: " + str(original_crc))

  #write new mst up to new file area
  mst_data_out.extend(mst_data[0:original_location])
  
  #write inserted file to mst
  mst_data_out.extend(insert_reader.read())

  #fill buffer
  add_buffer(mst_data_out)

  #write remainder of mst
  idx=roundup(original_location + original_length)
  mst_data_out.extend(mst_data[idx:])


  #fix table of contents 
  new_length = os.path.getsize(insert_file)
  mst_data_out[entry_location + 24: entry_location + 28] = struct.pack(pack_int,os.path.getsize(insert_file))


  #update every following files location
  idx=12
  file_count = int.from_bytes(mst_data[idx:idx+INT_BYTES], endian)
  idx+=INT_BYTES
  idx=27 * 4 # start of toc
  delta = roundup(new_length) - roundup(original_length)
  for i in range(file_count):
    name = mst_data[idx:idx+STR_BYTES]
    idx+=STR_BYTES
    location_offset = idx
    location = int.from_bytes(mst_data[idx:idx+INT_BYTES], endian)
    idx+=INT_BYTES
    length = int.from_bytes(mst_data[idx:idx+INT_BYTES], endian)
    idx+=INT_BYTES
    timestamp = int.from_bytes(mst_data[idx:idx+INT_BYTES], endian)
    idx+=INT_BYTES
    crc = int.from_bytes(mst_data[idx:idx+INT_BYTES], endian)
    idx+=INT_BYTES
    #if its a following file
    if location > original_location:
      mst_data_out[location_offset:location_offset+4] = struct.pack(pack_int,location+delta)

  return mst_data_out

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Insert a file into the MST")
  endian = parser.add_mutually_exclusive_group()
  endian.add_argument("-g", "--gamecube", help="Use gamecube endian - small endian", action="store_true")
  endian.add_argument("-x", "--xbox", help="Use xbox endian - big endian [Default]", action="store_true")
  parser.add_argument("mst", help="The MST")
  parser.add_argument("files", type=str, nargs='+', help="Files to insert into the mst")
  args = parser.parse_args()
  if args.gamecube:
    endian='big'
    pack_int = '>i'
  else:
    endian='little'
    pack_int = '<i'

  mst = args.mst
  mst_out = mst + ".new"
  mst_reader = open(mst, "rb")
  mst_data = mst_reader.read()
  mst_reader.close()
  
  mst_data = bytearray(mst_data)
  
  for i in range(len(args.files)):
    insert_file = args.files[i]
    insert_file_name = os.path.basename(insert_file)
    insert_reader = open(insert_file, "rb")

    mst_data = insert(mst_data, insert_file_name, insert_reader)
    insert_reader.close()

  mst_writer = open(mst_out, "wb")
  mst_writer.write(mst_data)
  
  #Fix mst size
  mst_writer.seek(8,os.SEEK_SET)
  new_size = os.path.getsize(mst_out)
  mst_writer.write(struct.pack(pack_int,new_size))
  
  mst_writer.close()


