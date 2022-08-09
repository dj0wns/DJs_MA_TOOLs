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

def entry_to_data(mst_data, idx):
  #read table entry
  name = mst_data[idx:idx+STR_BYTES]
  idx+=STR_BYTES
  location = int.from_bytes(mst_data[idx:idx+INT_BYTES], endian)
  idx+=INT_BYTES
  length = int.from_bytes(mst_data[idx:idx+INT_BYTES], endian)
  idx+=INT_BYTES
  timestamp = int.from_bytes(mst_data[idx:idx+INT_BYTES], endian)
  idx+=INT_BYTES
  crc = int.from_bytes(mst_data[idx:idx+INT_BYTES], endian)
  idx+=INT_BYTES
  return name, location, length, timestamp, crc, idx

def parse_mst_header(reader):
  global pack_int
  offset = reader.tell()
  reader.seek(0)
  mst = {}
  mst['signature'] = struct.unpack(pack_int, reader.read(4))[0]
  mst['version'] = struct.unpack(pack_int, reader.read(4))[0]
  mst['size'] = struct.unpack(pack_int, reader.read(4))[0]
  mst['num_entries'] = struct.unpack(pack_int, reader.read(4))[0]
  mst['num_free_entries'] = struct.unpack(pack_int, reader.read(4))[0]
  mst['num_support_entries'] = struct.unpack(pack_int, reader.read(4))[0]
  mst['num_free_support_entries'] = struct.unpack(pack_int, reader.read(4))[0]
  mst['data_offset'] = struct.unpack(pack_int, reader.read(4))[0]
  mst['tga_compiler_version'] = struct.unpack(pack_int, reader.read(4))[0]
  mst['ape_compiler_version'] = struct.unpack(pack_int, reader.read(4))[0]
  mst['mtx_compiler_version'] = struct.unpack(pack_int, reader.read(4))[0]
  mst['csv_compiler_version'] = struct.unpack(pack_int, reader.read(4))[0]
  mst['fnt_compiler_version'] = struct.unpack(pack_int, reader.read(4))[0]
  mst['sma_compiler_version'] = struct.unpack(pack_int, reader.read(4))[0]
  mst['gt_compiler_version'] = struct.unpack(pack_int, reader.read(4))[0]
  mst['wvb_compiler_version'] = struct.unpack(pack_int, reader.read(4))[0]
  mst['fpr_compiler_version'] = struct.unpack(pack_int, reader.read(4))[0]
  mst['cam_compiler_version'] = struct.unpack(pack_int, reader.read(4))[0]
  mst['reserved_1'] = struct.unpack(pack_int, reader.read(4))[0]
  mst['reserved_2'] = struct.unpack(pack_int, reader.read(4))[0]
  mst['reserved_3'] = struct.unpack(pack_int, reader.read(4))[0]
  mst['reserved_4'] = struct.unpack(pack_int, reader.read(4))[0]
  mst['reserved_5'] = struct.unpack(pack_int, reader.read(4))[0]
  mst['reserved_6'] = struct.unpack(pack_int, reader.read(4))[0]
  mst['reserved_7'] = struct.unpack(pack_int, reader.read(4))[0]
  mst['reserved_8'] = struct.unpack(pack_int, reader.read(4))[0]
  reader.seek(offset)
  return mst

def first_free_row_offset(mst_header):
  return 104+36*mst_header['num_entries'] #header size + row size * num entries

def roundup(x):
  return int(math.ceil(x / 4.0)) * 4

def add_buffer(data):
  current_offset = len(data)
  buffer_to_add = roundup(current_offset) - current_offset
  for i in range(buffer_to_add):
    data.append(0)


def add_table_entry(mst_data, insert_file, insert_file_name, insert_reader, mst_reader):
  mst_data_out = bytearray()
  mst_data_out.extend(mst_data) # we are appending at end so add all of the mst up to this point

  mst_header = parse_mst_header(mst_reader)
  # update relevant row
  row_offset = first_free_row_offset(mst_header)
  fname_bytes = insert_file_name.encode('ascii')
  insert_file_size = os.path.getsize(insert_file)
  mst_data_out[row_offset:row_offset + len(fname_bytes)] = fname_bytes #update name
  mst_data_out[row_offset + 20: row_offset + 24] = struct.pack(pack_int,len(mst_data_out)) #update location, we are appending to the end!
  mst_data_out[row_offset + 24: row_offset + 28] = struct.pack(pack_int,insert_file_size) #update size

  #update mst header, +1 entry, -1 free entry
  mst_data_out[12:16] = struct.pack(pack_int,mst_header['num_entries']+1)
  mst_data_out[16:20] = struct.pack(pack_int,mst_header['num_free_entries']-1)

  #write inserted file to mst
  mst_data_out.extend(insert_reader.read())

  #Align
  add_buffer(mst_data_out)

  print(f'Inserted {insert_file_name} with new row entry of {entry_to_data(mst_data_out, row_offset)}')

  return mst_data_out

def replace_table_entry(mst_data, insert_file, insert_file_name, insert_reader, idx):
  mst_data_out = bytearray()
  entry_location = idx

  original_name, original_location, original_length, original_timestamp, original_crc, idx = entry_to_data(mst_data, idx)

  print("Seek: " + str(idx))
  print("Original File: " + str(bytes(original_name).decode()) + ", location: " + str(original_location) + ", length: " + str(original_length) + ", timestamp: " + str(original_timestamp) + ", crc: " + str(original_crc))

  #write new mst up to new file area
  mst_data_out.extend(mst_data[0:original_location])

  #write inserted file to mst
  mst_data_out.extend(insert_reader.read())

  #fill buffer
  add_buffer(mst_data_out)

  #write remainder of mst
  idx=original_location + original_length
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
    location_offset = idx + STR_BYTES
    name, location, length, timestamp, crc, idx = entry_to_data(mst_data, idx)
    #if its a following file
    if location > original_location:
      mst_data_out[location_offset:location_offset+4] = struct.pack(pack_int,location+delta)

  return mst_data_out

def insert(mst_data, insert_file, insert_file_name, insert_reader, mst_reader):
  #search for file entry in mst
  b = bytearray()
  b.extend(map(ord, insert_file_name))
  idx = mst_data.find(b)

  if idx > 0:
    return replace_table_entry(mst_data, insert_file, insert_file_name, insert_reader, idx)
  else:
    return add_table_entry(mst_data, insert_file, insert_file_name, insert_reader, mst_reader)


def execute(is_big_endian, mst, files, output_suffix):
  global endian
  global pack_int
  if is_big_endian:
    endian='big'
    pack_int = '>i'
  else:
    endian='little'
    pack_int = '<i'

  mst_out = mst + output_suffix
  mst_reader = open(mst, "rb")
  mst_data = mst_reader.read()

  mst_data = bytearray(mst_data)

  for i in range(len(files)):
    insert_file = files[i]
    insert_file_name = os.path.basename(insert_file)
    insert_reader = open(insert_file, "rb")

    mst_data = insert(mst_data, insert_file, insert_file_name, insert_reader, mst_reader)
    insert_reader.close()

  mst_writer = open(mst_out, "wb")
  mst_writer.write(mst_data)

  #Fix mst size
  mst_writer.seek(8,os.SEEK_SET)
  new_size = os.path.getsize(mst_out)
  mst_writer.write(struct.pack(pack_int,new_size))

  mst_writer.close()

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Insert a file into the MST")
  endian = parser.add_mutually_exclusive_group()
  endian.add_argument("-g", "--gamecube", help="Use gamecube endian - small endian", action="store_true")
  endian.add_argument("-x", "--xbox", help="Use xbox endian - big endian [Default]", action="store_true")
  parser.add_argument("-s", "--suffix",  help="The suffix for the new mst. Is '.new' by default. If this is blank it will overwrite the mst.", default=".new")
  parser.add_argument("mst", help="The MST")
  parser.add_argument("files", type=str, nargs='+', help="Files to insert into the mst")
  args = parser.parse_args()
  execute(args.gamecube, args.mst, args.files, args.suffix)


