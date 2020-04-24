import sys
import os
import shutil
import struct
import math
import json
import jsonpickle
import argparse
import operator

#set of ma specific classes
from lib import ma_util, sma_classes, sma_functions

endian='little'
float_endian = '<f'
int_endian = '<i'
short_endian = '<h'
delimiter = '+'

fpath=os.path.realpath(__file__)
py_path=os.path.dirname(fpath)

def print_classes(header, public_functions, native_functions, libraries, public_variables, public_tagnames, data):
  header.print_data()
  print("---- Public Functions ----")
  for function in public_functions:
    function.print_data()
    for ins in function.data['instructions']:
      ins.print_data()
  print("---- Native Functions ----")
  for function in native_functions:
    function.print_data()
  print("---- Libraries ----")
  for function in libraries:
    function.print_data()
  print("---- Public Variables ----")
  for function in public_variables:
    function.print_data()
  print("---- Public tagnames ----")
  for function in public_tagnames:
    function.print_data()

def parse_sma_file(reader):
  header = sma_classes.AMXHeader(reader) 
  #next public functions
  public_functions = []
  reader.seek(header.data['public_functions_offset'])
  for i in range(header.data['num_public_functions']):
    public_functions.append(sma_classes.AMXFunctionStub(reader))
  #next native functions
  native_functions = []
  reader.seek(header.data['native_functions_offset'])
  for i in range(header.data['num_native_functions']):
    native_functions.append(sma_classes.AMXFunctionStub(reader))
  #next libraries
  libraries = []
  reader.seek(header.data['libraries_offset'])
  for i in range(header.data['num_libraries']):
    libraries.append(sma_classes.AMXFunctionStub(reader))
  #next public_variables
  public_variables = []
  reader.seek(header.data['public_variables_offset'])
  for i in range(header.data['num_public_variables']):
    public_variables.append(sma_classes.AMXFunctionStub(reader))
  #last public_tagnames
  public_tagnames = []
  reader.seek(header.data['public_tagnames_offset'])
  for i in range(header.data['num_public_tagnames']):
    public_tagnames.append(sma_classes.AMXFunctionStub(reader))

  #next get instructions i guess
  #read instructions block into memory for decompression
  #read rest of code and see where it gets you
  reader.seek(header.data['code_block_offset'])
  codestring = bytearray(reader.read())
  expanded_code = sma_functions.expand(codestring,
      header.data['size'] - header.data['code_block_offset'],
      header.data['heap_start'] - header.data['code_block_offset'])

  print(len(expanded_code))
  sorted_public_functions = sorted(public_functions, key=lambda item:item.data['address'])
  instructions = []
    #in this instance a public function is a set of instructions, so split instructions into functions
  #dirty hack to pass int by reference so that it can be modified by the constructor
  index = [0]
  function_index = 0
  while index[0] < header.data['data_block_offset'] - header.data['code_block_offset']:
    instructions.append(sma_classes.AMXInstruction(expanded_code, index))
    if function_index+1 != len(sorted_public_functions) \
        and index[0] >= sorted_public_functions[function_index+1].data['address']:
      sorted_public_functions[function_index].set_instructions(instructions)
      instructions = []
      function_index += 1
  #make sure to add last functions instructions
  sorted_public_functions[function_index].set_instructions(instructions)
 
  #read rest into data
  data = expanded_code[index[0]:]

  return header, sorted_public_functions, native_functions, libraries, public_variables, public_tagnames, data

def export_to_file(writer, header, public_functions, native_functions, libraries, public_variables, public_tagnames, data):
 
  writer.write(header.to_bytes())
  #update function offsets
  offset = 0
  for func in public_functions:
    func.data['address'] = offset
    offset += func.ins_size()
  #update header values
  header.data['num_public_functions'] = len(public_functions)
  header.data['num_native_functions'] = len(native_functions)
  header.data['num_libraries'] = len(libraries)
  header.data['num_public_variables'] = len(public_variables)
  header.data['num_public_tagnames'] = len(public_tagnames)
    
	#public functions are sorted by name for table references for whatever reason
  alpha_sorted_public_functions = sorted(public_functions, key=lambda item:item.data['name'])
  header.data['public_functions_offset'] = writer.tell()
  for func in alpha_sorted_public_functions:
    writer.write(func.to_bytes())
  header.data['native_functions_offset'] = writer.tell()
  for func in native_functions:
    writer.write(func.to_bytes())
  header.data['libraries_offset'] = writer.tell()
  for func in libraries:
    writer.write(func.to_bytes())
  header.data['public_variables_offset'] = writer.tell()
  for func in public_variables:
    writer.write(func.to_bytes())
  header.data['public_tagnames_offset'] = writer.tell()
  for func in public_tagnames:
    writer.write(func.to_bytes())
  
  #get codeblock size
  header.data['code_block_offset'] = writer.tell()
  header.data['data_block_offset'] = header.data['code_block_offset'] + offset

  #TODO research heap_start and stack_top - only things not updated
  header.data['heap_start'] = header.data['data_block_offset'] + header.data['heap_size']
  header.data['stack_top'] = header.data['heap_start'] + header.data['stack_size']

  #encode code
  for func in public_functions:
    for ins in func.data['instructions']:
      writer.write(ins.to_bytes())

        

  #encode data
  data_array = bytearray(data)
  #drop last byte i guess idk
  data_array = data_array[:-1]
  index = 0
  for index in range(0,len(data_array),4):
    to_write = sma_functions.encode_bin(data_array[index:], 1)
    #if last is null byte only do 1 byte i guess
    writer.write(to_write)
  
  #size
  header.data['size'] = writer.tell()
    
def export_to_folder(out_path, header, public_functions, native_functions, libraries, public_variables, public_tagnames, data):
  os.mkdir(out_path)
  
  header_file = open(os.path.join(out_path, "header.json"), "w")
  header_file.write(ma_util.pretty_pickle_json(header))
  header_file.close()
  
  native_functions_file = open(os.path.join(out_path, "native_functions.json"), "w")
  native_functions_file.write(ma_util.pretty_pickle_json(native_functions))
  native_functions_file.close()
  
  libraries_file = open(os.path.join(out_path, "libraries.json"), "w")
  libraries_file.write(ma_util.pretty_pickle_json(libraries))
  libraries_file.close()
  
  public_variables_file = open(os.path.join(out_path, "public_variables.json"), "w")
  public_variables_file.write(ma_util.pretty_pickle_json(public_variables))
  public_variables_file.close()
  
  public_tagnames_file = open(os.path.join(out_path, "public_tagnames.json"), "w")
  public_tagnames_file.write(ma_util.pretty_pickle_json(public_tagnames))
  public_tagnames_file.close()
  
  data_file = open(os.path.join(out_path, "data.dat"), "wb")
  data_file.write(data)
  data_file.close()
  
  #write disass files
  for i in range(len(public_functions)):
    fname = "publicfunction" + delimiter + str(i).zfill(3) + delimiter + public_functions[i].data['name'] + ".disass"
    f = open(os.path.join(out_path, fname), "w") 
    relative_line = [0]

    for instruction in public_functions[i].data['instructions']:
      f.write(instruction.to_string(relative_line))
    f.close()

def import_from_folder(directory):
  public_functions = []
  public_func_files = []

  for filename in os.listdir(directory):
    filepath = os.path.join(directory, filename)
    if filename == "header.json":
      header = jsonpickle.decode(open(filepath, "rb").read())
    elif filename == "native_functions.json":
      native_functions = jsonpickle.decode(open(filepath, "rb").read())
    elif filename == "libraries.json":
      libraries = jsonpickle.decode(open(filepath, "rb").read())
    elif filename == "public_variables.json":
      public_variables = jsonpickle.decode(open(filepath, "rb").read())
    elif filename == "public_tagnames.json":
      public_tagnames = jsonpickle.decode(open(filepath, "rb").read())
    elif filename == "data.dat":
      data = open(filepath, "rb").read()
    elif "publicfunction" + delimiter in filename:
      public_func_files.append(filename)
 
  public_func_files.sort()

  for filename in public_func_files:
    filepath = os.path.join(directory, filename)
    tags = filename.split(delimiter)
    function = sma_classes.AMXFunctionStub(None, -1, tags[2].split('.')[0])
    instructions = []
    reader = open(filepath, "rb")
    line = reader.readline()
    while line:
      instructions.append(sma_classes.AMXInstruction(line, -1)) 
      line = reader.readline()
    function.set_instructions(instructions)
    public_functions.append(function)

  return header, public_functions, native_functions, libraries, public_variables, public_tagnames, data

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Extract or rebuild a sma file")
  #endian = parser.add_mutually_exclusive_group()
  #endian.add_argument("-g", "--gamecube", help="Use gamecube endian - small endian", action="store_true")
  #endian.add_argument("-x", "--xbox", help="Use xbox endian - big endian [Default]", action="store_true")
  operation = parser.add_mutually_exclusive_group()
  operation.add_argument("-e", "--extract", help="Extract the contents of a sma file to a directory", action="store_true")
  operation.add_argument("-r", "--rebuild", help="Rebuild a sma file from a folder full of extracted files", action="store_true")
  parser.add_argument("-p", "--print", help="Print the structures to stdout", action="store_true")
  parser.add_argument("input", help="input file or folder")
  parser.add_argument("output", help="output file or folder")
  args = parser.parse_args()

  #sma always seems to be little endian

  #get input
  if args.extract:
    path = args.input
    reader = open(path, "rb")
    header, public_functions, native_functions, libraries, public_variables, public_tagnames, data = parse_sma_file(reader)
  elif args.rebuild:
    header, public_functions, native_functions, libraries, public_variables, public_tagnames, data = import_from_folder(args.input)
  else:
    print("Must specify extract or rebuild")
    sys.exit()
  
  if args.print:
    print_classes(header, public_functions, native_functions, libraries, public_variables, public_tagnames, data)

  if args.extract:
    export_to_folder(args.output, header, public_functions, native_functions, libraries, public_variables, public_tagnames, data)
  elif args.rebuild:
    path = args.output
    writer = open(path, "wb")
    #generate twice to update indices
    export_to_file(writer, header, public_functions, native_functions, libraries, public_variables, public_tagnames, data)
    writer.close()
    writer = open(path, "wb")
    export_to_file(writer, header, public_functions, native_functions, libraries, public_variables, public_tagnames, data)
    writer.close()
