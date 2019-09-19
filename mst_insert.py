import sys
import os
import shutil
import re
import glob
import struct
import math
import collections


fpath=os.path.realpath(__file__)
py_path=os.path.dirname(fpath)
pack_int = '<i'

#A dirty file injector for msts

def roundup(x):
#  return int(math.ceil(x / 16.0)) * 16
  return x

def add_buffer(writer):
  current_offset = writer.tell()
  buffer_to_add = roundup(current_offset) - current_offset
  for i in range(buffer_to_add):
    writer.write(struct.pack('B', 0))


if __name__ == '__main__':
  if len(sys.argv) < 3 :
    print("Requires a file then an mst as arguments")
    sys.exit()

  insert_file = sys.argv[1]
  insert_file_name = os.path.basename(insert_file)
  mst = sys.argv[2]
  mst_out = mst + ".new"
  insert_reader = open(insert_file, "rb")
  mst_reader = open(mst, "rb")
  mst_writer = open(mst_out, "wb")

 
  #read mst into memory because laziness
  mst_data = mst_reader.read()
  
  #search for file entry in mst
  b = bytearray()
  b.extend(map(ord, insert_file_name))
  idx = mst_data.find(b)

  #free up some ram
  del mst_data

  #read table entry
  mst_reader.seek(idx, os.SEEK_SET)
  original_name = mst_reader.read(20)
  original_location = int.from_bytes(mst_reader.read(4), "little")
  original_length = int.from_bytes(mst_reader.read(4), "little")
  original_timestamp = int.from_bytes(mst_reader.read(4), "little")
  original_crc = int.from_bytes(mst_reader.read(4), "little")

  print("Seek: " + str(idx))
  print("Original File: " + str(original_name) + ", location: " + str(original_location) + ", length: " + str(original_length) + ", timestamp: " + str(original_timestamp) + ", crc: " + str(original_crc))

  #write new mst up to new file area
  mst_reader.seek(0, os.SEEK_SET)
  mst_data = mst_reader.read(original_location)
  mst_writer.write(mst_data)
  del mst_data
  
  #write inserted file to mst
  insert_data = insert_reader.read()
  mst_writer.write(insert_data)
  del insert_data

  #fill buffer
  add_buffer(mst_writer)

  #write remainder of mst
  mst_reader.seek(roundup(original_location + original_length), os.SEEK_SET)
  mst_data = mst_reader.read()
  mst_writer.write(mst_data)
  del mst_data

  #Fix mst size
  mst_writer.seek(8,os.SEEK_SET)
  new_size = os.path.getsize(mst_out)
  mst_writer.write(struct.pack(pack_int,new_size))

  #fix table of contents 
  #TODO update every following entry due to new size
  mst_writer.seek(idx + 24,os.SEEK_SET)
  new_length = os.path.getsize(insert_file)
  mst_writer.write(struct.pack(pack_int,new_length))


  #update every following files location
  mst_reader.seek(12,os.SEEK_SET)
  file_count = int.from_bytes(mst_reader.read(4), "little")
  mst_reader.seek(27 * 4,os.SEEK_SET) # start of toc
  delta = roundup(new_length) - roundup(original_length)
  first = 99999999999
  last = 0
  for i in range(file_count):
    name = mst_reader.read(20)
    mst_writer.seek(mst_reader.tell())
    location = int.from_bytes(mst_reader.read(4), "little")
    length = int.from_bytes(mst_reader.read(4), "little")
    timestamp = int.from_bytes(mst_reader.read(4), "little")
    crc = int.from_bytes(mst_reader.read(4), "little")
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
  mst_reader.seek(idx, os.SEEK_SET)
  name = mst_reader.read(20)
  location = int.from_bytes(mst_reader.read(4), "little")
  length = int.from_bytes(mst_reader.read(4), "little")
  timestamp = int.from_bytes(mst_reader.read(4), "little")
  crc = int.from_bytes(mst_reader.read(4), "little")

  print("New File: " + str(name) + ", location: " + str(location) + ", length: " + str(length) + ", timestamp: " + str(timestamp) + ", crc: " + str(crc))


