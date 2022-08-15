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
NUM_ENTRIES_OFFSET = 12
NUM_FREE_ENTRIES_OFFSET=16
ENTRY_LOCATION_OFFSET = 20
ENTRY_SIZE_OFFSET = 24

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

def parse_mst_header(data):
  global pack_int
  mst = {}
  idx = 0
  mst['signature'] = struct.unpack(pack_int, data[idx:idx+4])[0]
  idx += 4
  mst['version'] = struct.unpack(pack_int, data[idx:idx+4])[0]
  idx += 4
  mst['size'] = struct.unpack(pack_int, data[idx:idx+4])[0]
  idx += 4
  mst['num_entries'] = struct.unpack(pack_int, data[idx:idx+4])[0]
  idx += 4
  mst['num_free_entries'] = struct.unpack(pack_int, data[idx:idx+4])[0]
  idx += 4
  mst['num_support_entries'] = struct.unpack(pack_int, data[idx:idx+4])[0]
  idx += 4
  mst['num_free_support_entries'] = struct.unpack(pack_int, data[idx:idx+4])[0]
  idx += 4
  mst['data_offset'] = struct.unpack(pack_int, data[idx:idx+4])[0]
  idx += 4
  mst['tga_compiler_version'] = struct.unpack(pack_int, data[idx:idx+4])[0]
  idx += 4
  mst['ape_compiler_version'] = struct.unpack(pack_int, data[idx:idx+4])[0]
  idx += 4
  mst['mtx_compiler_version'] = struct.unpack(pack_int, data[idx:idx+4])[0]
  idx += 4
  mst['csv_compiler_version'] = struct.unpack(pack_int, data[idx:idx+4])[0]
  idx += 4
  mst['fnt_compiler_version'] = struct.unpack(pack_int, data[idx:idx+4])[0]
  idx += 4
  mst['sma_compiler_version'] = struct.unpack(pack_int, data[idx:idx+4])[0]
  idx += 4
  mst['gt_compiler_version'] = struct.unpack(pack_int, data[idx:idx+4])[0]
  idx += 4
  mst['wvb_compiler_version'] = struct.unpack(pack_int, data[idx:idx+4])[0]
  idx += 4
  mst['fpr_compiler_version'] = struct.unpack(pack_int, data[idx:idx+4])[0]
  idx += 4
  mst['cam_compiler_version'] = struct.unpack(pack_int, data[idx:idx+4])[0]
  idx += 4
  mst['reserved_1'] = struct.unpack(pack_int, data[idx:idx+4])[0]
  idx += 4
  mst['reserved_2'] = struct.unpack(pack_int, data[idx:idx+4])[0]
  idx += 4
  mst['reserved_3'] = struct.unpack(pack_int, data[idx:idx+4])[0]
  idx += 4
  mst['reserved_4'] = struct.unpack(pack_int, data[idx:idx+4])[0]
  idx += 4
  mst['reserved_5'] = struct.unpack(pack_int, data[idx:idx+4])[0]
  idx += 4
  mst['reserved_6'] = struct.unpack(pack_int, data[idx:idx+4])[0]
  idx += 4
  mst['reserved_7'] = struct.unpack(pack_int, data[idx:idx+4])[0]
  idx += 4
  mst['reserved_8'] = struct.unpack(pack_int, data[idx:idx+4])[0]
  return mst

def catalog_entries(mst):
  header = parse_mst_header(mst)
  entry_array = []
  for i in range(header['num_entries']):
    name = entry_to_data(mst, entry_index_to_offset(i))[0]
    entry_array.append(name.decode('ascii', 'backslashreplace').split("\x00")[0]) #split on null byte to separate the null terminated string
  return entry_array

def write_mst_string(mst, offset, data):
  mst[offset:offset+len(data)] = data

def write_mst_int(mst, offset, data):
  mst[offset:offset+INT_BYTES] = struct.pack(pack_int, data)

def entry_index_to_offset(index):
  return 108+36*index #header size + row size * num entries

def first_free_row_offset(mst_header):
  return entry_index_to_offset(mst_header['num_entries'])

def roundup(x):
  return int(math.ceil(x / 4.0)) * 4

def add_buffer(data):
  current_offset = len(data)
  buffer_to_add = roundup(current_offset) - current_offset
  for i in range(buffer_to_add):
    data.append(0)


def add_table_entry(mst_data, insert_file, insert_file_name, insert_reader):
  mst_header = parse_mst_header(mst_data)

  #update mst header, +1 entry, -1 free entry
  write_mst_int(mst_data, NUM_ENTRIES_OFFSET, mst_header['num_entries']+1)
  write_mst_int(mst_data, NUM_FREE_ENTRIES_OFFSET, mst_header['num_entries']+1)

  original_size = len(mst_data)
  #write inserted file to mst
  mst_data.extend(insert_reader.read())

  #Align
  add_buffer(mst_data)

  file_size = len(mst_data) - original_size

  # update relevant row
  row_offset = first_free_row_offset(mst_header)
  fname_bytes = insert_file_name.encode('ascii')
  write_mst_string(mst_data, row_offset, fname_bytes)
  write_mst_int(mst_data, row_offset + ENTRY_LOCATION_OFFSET, original_size)
  write_mst_int(mst_data, row_offset + ENTRY_SIZE_OFFSET, file_size)

  print(f'Inserted {insert_file_name} with new row entry of {entry_to_data(mst_data, row_offset)}')

  return mst_data

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

  #get resulting file length
  new_length = len(mst_data_out) - original_location

  #write remainder of mst
  idx=original_location + original_length
  mst_data_out.extend(mst_data[idx:])

  #fix table of contents
  write_mst_int(mst_data_out, entry_location + ENTRY_SIZE_OFFSET, new_length)

  #update every following files location
  idx=12
  file_count = int.from_bytes(mst_data[idx:idx+INT_BYTES], endian)
  delta = new_length - original_length
  print (file_count)
  for i in range(file_count):
    entry_offset = entry_index_to_offset(i)
    name, location, length, timestamp, crc, idx = entry_to_data(mst_data, entry_offset)
    #if its a following file
    if location > original_location:
      write_mst_int(mst_data_out, entry_offset + ENTRY_LOCATION_OFFSET, location+delta)

  return mst_data_out

def insert(mst_data, insert_file, insert_file_name, insert_reader, entries):
  print(insert_file_name)
  if insert_file_name in entries:
    idx = entries.index(insert_file_name)
    return replace_table_entry(mst_data, insert_file, insert_file_name, insert_reader, entry_index_to_offset(idx))
  else:
    return add_table_entry(mst_data, insert_file, insert_file_name, insert_reader)

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
  print(parse_mst_header(mst_data))
  entries = catalog_entries(mst_data)

  for i in range(len(files)):
    insert_file = files[i]
    insert_file_name = os.path.basename(insert_file)
    insert_reader = open(insert_file, "rb")

    mst_data = insert(mst_data, insert_file, insert_file_name, insert_reader, entries)
    insert_reader.close()

  mst_writer = open(mst_out, "wb")
  mst_writer.write(mst_data)

  #Fix mst size
  mst_writer.seek(8,os.SEEK_SET)
  new_size = os.path.getsize(mst_out)
  print(new_size)
  print(parse_mst_header(mst_data))
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


