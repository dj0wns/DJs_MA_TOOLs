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
header_size = 44



def roundup(x):
  return int(math.ceil(x / 16.0)) * 16

def add_buffer(writer):
  current_offset = writer.tell()
  buffer_to_add = roundup(current_offset) - current_offset
  for i in range(buffer_to_add):
    writer.write(struct.pack('B', 0))


if __name__ == '__main__':
  if len(sys.argv) < 2 : 
    print("Requires a folder as an argument")
    sys.exit()

  #set up writer
  in_folder = sys.argv[1]
  in_folder_name = os.path.dirname(in_folder)
  file_out = os.path.join(py_path, in_folder_name + ".wld")
  writer = open(file_out, "wb")
  
  #set up file addresses
  first_part_suffix = os.path.join(in_folder,"First_Part_Suffix")
  second_file = os.path.join(in_folder,"Second_Part")
  third_file = os.path.join(in_folder,"Third_Part")
  fourth_file = os.path.join(in_folder,"Fourth_Part")

  #set up file input list
  file_pattern = os.path.join(in_folder,'[0-9][0-9][0-9]')
  files = glob.glob(file_pattern)

  #build ape file table
  file_dict = collections.OrderedDict()
  offset = roundup(header_size + len(files) * 8)
  init_offset = offset
  for f in sorted(files):
    offset = roundup(offset)
    size = os.path.getsize(f)
    file_dict[offset] = size
    offset = offset + size #dont round here so you can use offset for length

  #write header1
  writer.write(struct.pack(pack_int,0)) # wld size will add once known
  writer.write(struct.pack(pack_int,len(files))) # ape file count
  writer.write(struct.pack(pack_int,header_size)) # header size - always 44 i believe
  #start offsets of the first 4 parts remember to round to nearest hex

  #write start and end of first part
  first_start = header_size + len(files) * 4 # this points to the start of the lengths table for the ape files
  first_len = offset - init_offset #where actual length seems to not include the lengths
  writer.write(struct.pack(pack_int,first_start)) 
  writer.write(struct.pack(pack_int,first_len)) 

  #write start and end of second part
  second_start = roundup(roundup(header_size + len(files) * 8) + first_len) #have to recalculate first start because aforementioned bug
  second_len = os.path.getsize(second_file)
  writer.write(struct.pack(pack_int,second_start)) 
  writer.write(struct.pack(pack_int,second_len)) 
  
  #write start and end of third part
  third_start = roundup(second_start + second_len) #have to recalculate first start because aforementioned bug
  third_len = os.path.getsize(third_file)
  writer.write(struct.pack(pack_int,third_start)) 
  writer.write(struct.pack(pack_int,third_len)) 

  #write start and end of fourth part
  fourth_start = roundup(third_start + third_len) #have to recalculate first start because aforementioned bug
  fourth_len = os.path.getsize(fourth_file)
  writer.write(struct.pack(pack_int,fourth_start)) 
  writer.write(struct.pack(pack_int,fourth_len)) 

  #add in ape file listing - offsets first then lengths
  for offset, length in file_dict.items():
    writer.write(struct.pack(pack_int,offset)) 
  for offset, length in file_dict.items():
    writer.write(struct.pack(pack_int,length)) 

  #initial buffers
  current_offset = writer.tell()
  buffer_to_add = roundup(current_offset) - current_offset
  for i in range(buffer_to_add):
    writer.write(struct.pack('B', 0))

  #now append files
  for f in sorted(files)[:-1]:
    with open(f, "rb") as ape:
        data = ape.read()
    writer.write(data)
    #add buffer but not if last file
    add_buffer(writer)

  #append last file but dont buffer
  final_file = sorted(files)[-1]
  with open(final_file, "rb") as ape:
      data = ape.read()
  writer.write(data)

  
  #append first part suffix - buffer should be set properly
  with open(first_part_suffix, "rb") as f:
    data = f.read()
  writer.write(data)
  add_buffer(writer)

  #append second - buffer should be set properly
  with open(second_file, "rb") as f:
    data = f.read()
  writer.write(data)
  add_buffer(writer)
  
  #append third - buffer should be set properly
  with open(third_file, "rb") as f:
    data = f.read()
  writer.write(data)
  add_buffer(writer)

  #append fourth - buffer should be set properly
  with open(fourth_file, "rb") as f:
    data = f.read()
  writer.write(data)

  #write size to beginning of file
  writer.seek(0)
  writer.write(struct.pack(pack_int, os.path.getsize(file_out)))
