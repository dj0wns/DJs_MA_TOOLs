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

def add_buffer(writer):
  current_offset = writer.tell()
  buffer_to_add = roundup(current_offset) - current_offset
  for i in range(buffer_to_add):
    writer.write(struct.pack('B', 0))

def insert(mst_data, mst_out, out_writer, insert_file_name, insert_reader):
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
  out_mst_data = mst_data[0:original_location]
  mst_writer.write(out_mst_data)
  del out_mst_data
  
  #write inserted file to mst
  insert_data = insert_reader.read()
  mst_writer.write(insert_data)
  del insert_data

  #fill buffer
  add_buffer(mst_writer)

  #write remainder of mst
  idx=roundup(original_location + original_length)
  out_mst_data = mst_data[idx:]
  mst_writer.write(out_mst_data)

  #Fix mst size
  mst_writer.seek(8,os.SEEK_SET)
  new_size = os.path.getsize(mst_out)
  mst_writer.write(struct.pack(pack_int,new_size))

  #fix table of contents 
  #TODO update every following entry due to new size
  mst_writer.seek(entry_location + 24,os.SEEK_SET)
  new_length = os.path.getsize(insert_file)
  mst_writer.write(struct.pack(pack_int,new_length))


  #update every following files location
  idx=12
  file_count = int.from_bytes(mst_data[idx:idx+INT_BYTES], endian)
  idx+=INT_BYTES
  idx=27 * 4 # start of toc
  delta = roundup(new_length) - roundup(original_length)
  first = 99999999999
  last = 0
  for i in range(file_count):
    name = mst_data[idx:idx+STR_BYTES]
    idx+=STR_BYTES
    mst_writer.seek(idx)
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
      mst_writer.write(struct.pack(pack_int,location+delta))
    
    if location < first:
      first = location
    if location + length > last:
      last = location + length 
    
  
  print(str(first) + " - " + str(last))
  mst_writer.close()
  

  #print new entry
  mst_reader = open(mst_out, "rb")
  mst_reader.seek(entry_location, os.SEEK_SET)
  name = mst_reader.read(20)
  location = int.from_bytes(mst_reader.read(4), endian)
  length = int.from_bytes(mst_reader.read(4), endian)
  timestamp = int.from_bytes(mst_reader.read(4), endian)
  crc = int.from_bytes(mst_reader.read(4), endian)

  print("New File: " + str(bytes(name).decode()) + ", location: " + str(location) + ", length: " + str(length) + ", timestamp: " + str(timestamp) + ", crc: " + str(crc))

  mst_reader.close()


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
  
  for i in range(len(args.files)):
    insert_file = args.files[i]
    insert_file_name = os.path.basename(insert_file)
    print(insert_file_name)
    insert_reader = open(insert_file, "rb")
    if i == 0:   
      mst_reader = open(mst, "rb")
    else:
      #we are just overwriting the new until it is correct
      mst_reader = open(mst_out, "rb")
    
    mst_data = mst_reader.read()
    mst_reader.close()
    mst_data = bytearray(mst_data)
    
    mst_writer = open(mst_out, "wb")
    mst_writer.seek(0)
  
    insert(mst_data, mst_out, mst_writer, insert_file_name, insert_reader)
    mst_writer.close()
    insert_reader.close()
    del mst_data



