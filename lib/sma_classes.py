import struct
import os
import sys
import json
import math
from enum import Enum

from . import ma_util, sma_functions

#entries and data types from smallamx - now known as pawn. A c-like scripting engine

#globals because i dont want to rewrite this - make sure to set them to the correct value - xbox default
endian='little'
float_endian = '<f'
int_endian = '<i'
uint_endian = '<I'
short_endian = '<H'
op_len = 4
arg_len = 4

class Labels(Enum):
  OP_NONE = 0
  OP_LOAD_PRI = 1
  OP_LOAD_ALT = 2
  OP_LOAD_S_PRI = 3
  OP_LOAD_S_ALT = 4
  OP_LREF_PRI = 5
  OP_LREF_ALT = 6
  OP_LREF_S_PRI = 7
  OP_LREF_S_ALT = 8
  OP_LOAD_I = 9
  OP_LODB_I = 10
  OP_CONST_PRI = 11
  OP_CONST_ALT = 12
  OP_ADDR_PRI = 13
  OP_ADDR_ALT = 14
  OP_STOR_PRI = 15
  OP_STOR_ALT = 16
  OP_STOR_S_PRI = 17
  OP_STOR_S_ALT = 18
  OP_SREF_PRI = 19
  OP_SREF_ALT = 20
  OP_SREF_S_PRI = 21
  OP_SREF_S_ALT = 22
  OP_STOR_I = 23
  OP_STRB_I = 24
  OP_LIDX = 25
  OP_LIDX_B = 26
  OP_IDXADDR = 27
  OP_IDXADDR_B = 28
  OP_ALIGN_PRI = 29
  OP_ALIGN_ALT = 30
  OP_LCTRL = 31
  OP_SCTRL = 32
  OP_MOVE_PRI = 33
  OP_MOVE_ALT = 34
  OP_XCHG = 35
  OP_PUSH_PRI = 36
  OP_PUSH_ALT = 37
  OP_PUSH_R = 38
  OP_PUSH_C = 39
  OP_PUSH = 40
  OP_PUSH_S = 41
  OP_POP_PRI = 42
  OP_POP_ALT = 43
  OP_STACK = 44
  OP_HEAP = 45
  OP_PROC = 46
  OP_RET = 47
  OP_RETN = 48
  OP_CALL = 49
  OP_CALL_PRI = 50
  OP_JUMP = 51
  OP_JREL = 52
  OP_JZER = 53
  OP_JNZ = 54
  OP_JEQ = 55
  OP_JNEQ = 56
  OP_JLESS = 57
  OP_JLEQ = 58
  OP_JGRTR = 59
  OP_JGEQ = 60
  OP_JSLESS = 61
  OP_JSLEQ = 62
  OP_JSGRTR = 63
  OP_JSGEQ = 64
  OP_SHL = 65
  OP_SHR = 66
  OP_SSHR = 67
  OP_SHL_C_PRI = 68
  OP_SHL_C_ALT = 69
  OP_SHR_C_PRI = 70
  OP_SHR_C_ALT = 71
  OP_SMUL = 72
  OP_SDIV = 73
  OP_SDIV_ALT = 74
  OP_UMUL = 75
  OP_UDIV = 76
  OP_UDIV_ALT = 77
  OP_ADD = 78
  OP_SUB = 79
  OP_SUB_ALT = 80
  OP_AND = 81
  OP_OR = 82
  OP_XOR = 83
  OP_NOT = 84
  OP_NEG = 85
  OP_INVERT = 86
  OP_ADD_C = 87
  OP_SMUL_C = 88
  OP_ZERO_PRI = 89
  OP_ZERO_ALT = 90
  OP_ZERO = 91
  OP_ZERO_S = 92
  OP_SIGN_PRI = 93
  OP_SIGN_ALT = 94
  OP_EQ = 95
  OP_NEQ = 96
  OP_LESS = 97
  OP_LEQ = 98
  OP_GRTR = 99
  OP_GEQ = 100
  OP_SLESS = 101
  OP_SLEQ = 102
  OP_SGRTR = 103
  OP_SGEQ = 104
  OP_EQ_C_PRI = 105
  OP_EQ_C_ALT = 106
  OP_INC_PRI = 107
  OP_INC_ALT = 108
  OP_INC = 109
  OP_INC_S = 110
  OP_INC_I = 111
  OP_DEC_PRI = 112
  OP_DEC_ALT = 113
  OP_DEC = 114
  OP_DEC_S = 115
  OP_DEC_I = 116
  OP_MOVS = 117
  OP_CMPS = 118
  OP_FILL = 119
  OP_HALT = 120
  OP_BOUNDS = 121
  OP_SYSREQ_PRI = 122
  OP_SYSREQ_C = 123
  OP_FILE = 124
  OP_LINE = 125
  OP_SYMBOL = 126
  OP_SRANGE = 127
  OP_JUMP_PRI = 128
  OP_SWITCH = 129
  OP_CASETBL = 130
  OP_SWAP_PRI = 131
  OP_SWAP_ALT = 132
  OP_PUSHADDR = 133

class label_data:
  def __init__(self, argcount):
    self.argcount = argcount
  

label_enum_to_data = {
  Labels.OP_NONE : label_data(0),
  Labels.OP_LOAD_PRI : label_data(1),
  Labels.OP_LOAD_ALT : label_data(1),
  Labels.OP_LOAD_S_PRI : label_data(1),
  Labels.OP_LOAD_S_ALT : label_data(1),
  Labels.OP_LREF_PRI : label_data(1),
  Labels.OP_LREF_ALT : label_data(1),
  Labels.OP_LREF_S_PRI : label_data(1),
  Labels.OP_LREF_S_ALT : label_data(1),
  Labels.OP_LOAD_I : label_data(0),
  Labels.OP_LODB_I : label_data(1),
  Labels.OP_CONST_PRI : label_data(1),
  Labels.OP_CONST_ALT : label_data(1),
  Labels.OP_ADDR_PRI : label_data(1),
  Labels.OP_ADDR_ALT : label_data(1),
  Labels.OP_STOR_PRI : label_data(1),
  Labels.OP_STOR_ALT : label_data(1),
  Labels.OP_STOR_S_PRI : label_data(1),
  Labels.OP_STOR_S_ALT : label_data(1),
  Labels.OP_SREF_PRI : label_data(1),
  Labels.OP_SREF_ALT : label_data(1),
  Labels.OP_SREF_S_PRI : label_data(1),
  Labels.OP_SREF_S_ALT : label_data(1),
  Labels.OP_STOR_I : label_data(0),
  Labels.OP_STRB_I : label_data(1),
  Labels.OP_LIDX : label_data(0),
  Labels.OP_LIDX_B : label_data(1),
  Labels.OP_IDXADDR : label_data(0),
  Labels.OP_IDXADDR_B : label_data(1),
  Labels.OP_ALIGN_PRI : label_data(1),
  Labels.OP_ALIGN_ALT : label_data(1),
  Labels.OP_LCTRL : label_data(1),
  Labels.OP_SCTRL : label_data(1),
  Labels.OP_MOVE_PRI : label_data(0),
  Labels.OP_MOVE_ALT : label_data(0),
  Labels.OP_XCHG : label_data(0),
  Labels.OP_PUSH_PRI : label_data(0),
  Labels.OP_PUSH_ALT : label_data(0),
  Labels.OP_PUSH_R : label_data(1),
  Labels.OP_PUSH_C : label_data(1),
  Labels.OP_PUSH : label_data(1),
  Labels.OP_PUSH_S : label_data(1),
  Labels.OP_POP_PRI : label_data(0),
  Labels.OP_POP_ALT : label_data(0),
  Labels.OP_STACK : label_data(1),
  Labels.OP_HEAP : label_data(1),
  Labels.OP_PROC : label_data(0),
  Labels.OP_RET : label_data(0),
  Labels.OP_RETN : label_data(0),
  Labels.OP_CALL : label_data(1),
  Labels.OP_CALL_PRI : label_data(0),
  Labels.OP_JUMP : label_data(1),
  Labels.OP_JREL : label_data(1),
  Labels.OP_JZER : label_data(1),
  Labels.OP_JNZ : label_data(1),
  Labels.OP_JEQ : label_data(1),
  Labels.OP_JNEQ : label_data(1),
  Labels.OP_JLESS : label_data(1),
  Labels.OP_JLEQ : label_data(1),
  Labels.OP_JGRTR : label_data(1),
  Labels.OP_JGEQ : label_data(1),
  Labels.OP_JSLESS : label_data(1),
  Labels.OP_JSLEQ : label_data(1),
  Labels.OP_JSGRTR : label_data(1),
  Labels.OP_JSGEQ : label_data(1),
  Labels.OP_SHL : label_data(0),
  Labels.OP_SHR : label_data(0),
  Labels.OP_SSHR : label_data(0),
  Labels.OP_SHL_C_PRI : label_data(1),
  Labels.OP_SHL_C_ALT : label_data(1),
  Labels.OP_SHR_C_PRI : label_data(1),
  Labels.OP_SHR_C_ALT : label_data(1),
  Labels.OP_SMUL : label_data(0),
  Labels.OP_SDIV : label_data(0),
  Labels.OP_SDIV_ALT : label_data(0),
  Labels.OP_UMUL : label_data(0),
  Labels.OP_UDIV : label_data(0),
  Labels.OP_UDIV_ALT : label_data(0),
  Labels.OP_ADD : label_data(0),
  Labels.OP_SUB : label_data(0),
  Labels.OP_SUB_ALT : label_data(0),
  Labels.OP_AND : label_data(0),
  Labels.OP_OR : label_data(0),
  Labels.OP_XOR : label_data(0),
  Labels.OP_NOT : label_data(0),
  Labels.OP_NEG : label_data(0),
  Labels.OP_INVERT : label_data(0),
  Labels.OP_ADD_C : label_data(1),
  Labels.OP_SMUL_C : label_data(1),
  Labels.OP_ZERO_PRI : label_data(0),
  Labels.OP_ZERO_ALT : label_data(0),
  Labels.OP_ZERO : label_data(1),
  Labels.OP_ZERO_S : label_data(1),
  Labels.OP_SIGN_PRI : label_data(0),
  Labels.OP_SIGN_ALT : label_data(0),
  Labels.OP_EQ : label_data(0),
  Labels.OP_NEQ : label_data(0),
  Labels.OP_LESS : label_data(0),
  Labels.OP_LEQ : label_data(0),
  Labels.OP_GRTR : label_data(0),
  Labels.OP_GEQ : label_data(0),
  Labels.OP_SLESS : label_data(0),
  Labels.OP_SLEQ : label_data(0),
  Labels.OP_SGRTR : label_data(0),
  Labels.OP_SGEQ : label_data(0),
  Labels.OP_EQ_C_PRI : label_data(1),
  Labels.OP_EQ_C_ALT : label_data(1),
  Labels.OP_INC_PRI : label_data(0),
  Labels.OP_INC_ALT : label_data(0),
  Labels.OP_INC : label_data(1),
  Labels.OP_INC_S : label_data(1),
  Labels.OP_INC_I : label_data(0),
  Labels.OP_DEC_PRI : label_data(0),
  Labels.OP_DEC_ALT : label_data(0),
  Labels.OP_DEC : label_data(1),
  Labels.OP_DEC_S : label_data(1),
  Labels.OP_DEC_I : label_data(0),
  Labels.OP_MOVS : label_data(1),
  Labels.OP_CMPS : label_data(1),
  Labels.OP_FILL : label_data(1),
  Labels.OP_HALT : label_data(1),
  Labels.OP_BOUNDS : label_data(1),
  Labels.OP_SYSREQ_PRI : label_data(0),
  Labels.OP_SYSREQ_C : label_data(1),
  Labels.OP_FILE : label_data(0),
  Labels.OP_LINE : label_data(2),
  Labels.OP_SYMBOL : label_data(0),
  Labels.OP_SRANGE : label_data(0),
  Labels.OP_JUMP_PRI : label_data(0),
  Labels.OP_SWITCH : label_data(1),
  Labels.OP_CASETBL : label_data(-1),
  Labels.OP_SWAP_PRI : label_data(0),
  Labels.OP_SWAP_ALT : label_data(0),
  Labels.OP_PUSHADDR : label_data(1)
}

last_function = ""

def int_array_to_string(arr):
  string = ""
  for i in range(0, len(arr),4):
    if not arr[i]:
      break;
    string += chr(arr[i])
  return string

class AMXHeader:
  def __init__(self, reader):
    self.data = {}
    self.data['size'] = int.from_bytes(reader.read(4), byteorder=endian, signed=False)
    self.data['magic_signature'] = int.from_bytes(reader.read(2), byteorder=endian, signed=False)
    self.data['file_version'] = int.from_bytes(reader.read(1), byteorder=endian, signed=False)
    self.data['amx_version'] = int.from_bytes(reader.read(1), byteorder=endian, signed=False)
    self.data['flags'] = int.from_bytes(reader.read(2), byteorder=endian, signed=False)
    self.data['defsize'] = int.from_bytes(reader.read(2), byteorder=endian, signed=False)
    self.data['code_block_offset'] = int.from_bytes(reader.read(4), byteorder=endian, signed=True)
    self.data['data_block_offset'] = int.from_bytes(reader.read(4), byteorder=endian, signed=True)
    self.data['heap_start'] = int.from_bytes(reader.read(4), byteorder=endian, signed=True)
    self.data['stack_top'] = int.from_bytes(reader.read(4), byteorder=endian, signed=True)
    self.data['instruction_pointer'] = int.from_bytes(reader.read(4), byteorder=endian, signed=True)
    self.data['num_public_functions'] = int.from_bytes(reader.read(2), byteorder=endian, signed=True)
    self.data['public_functions_offset'] = int.from_bytes(reader.read(4), byteorder=endian, signed=True)
    self.data['num_native_functions'] = int.from_bytes(reader.read(2), byteorder=endian, signed=True)
    self.data['native_functions_offset'] = int.from_bytes(reader.read(4), byteorder=endian, signed=True)
    self.data['num_libraries'] = int.from_bytes(reader.read(2), byteorder=endian, signed=True)
    self.data['libraries_offset'] = int.from_bytes(reader.read(4), byteorder=endian, signed=True)
    self.data['num_public_variables'] = int.from_bytes(reader.read(2), byteorder=endian, signed=True)
    self.data['public_variables_offset'] = int.from_bytes(reader.read(4), byteorder=endian, signed=True)
    self.data['num_public_tagnames'] = int.from_bytes(reader.read(2), byteorder=endian, signed=True)
    self.data['public_tagnames_offset'] = int.from_bytes(reader.read(4), byteorder=endian, signed=True)
    self.data['pad'] = int.from_bytes(reader.read(2), byteorder=endian, signed=True)

    #helper values
    self.data['heap_size'] = self.data['heap_start'] - self.data['data_block_offset']
    self.data['stack_size'] = self.data['stack_top'] - self.data['heap_start']
 

  def print_data(self):
    print("--------------- AMX Header ---------------")
    for item in self.data:
      print(item + " : " + str(self.data[item]))

  def size(self):
    size = 64 #header bytes
    return size;

  def to_bytes(self):
    bytes = struct.pack(int_endian, self.data['size'])
    bytes += struct.pack(short_endian, self.data['magic_signature'])
    bytes += self.data['file_version'].to_bytes(1,byteorder=endian)
    bytes += self.data['amx_version'].to_bytes(1,byteorder=endian)
    bytes += struct.pack(short_endian, self.data['flags'])
    bytes += struct.pack(short_endian, self.data['defsize'])
    bytes += struct.pack(int_endian, self.data['code_block_offset'])
    bytes += struct.pack(int_endian, self.data['data_block_offset'])
    bytes += struct.pack(int_endian, self.data['heap_start'])
    bytes += struct.pack(int_endian, self.data['stack_top'])
    bytes += struct.pack(int_endian, self.data['instruction_pointer'])
    bytes += struct.pack(short_endian, self.data['num_public_functions'])
    bytes += struct.pack(int_endian, self.data['public_functions_offset'])
    bytes += struct.pack(short_endian, self.data['num_native_functions'])
    bytes += struct.pack(int_endian, self.data['native_functions_offset'])
    bytes += struct.pack(short_endian, self.data['num_libraries'])
    bytes += struct.pack(int_endian, self.data['libraries_offset'])
    bytes += struct.pack(short_endian, self.data['num_public_variables'])
    bytes += struct.pack(int_endian, self.data['public_variables_offset'])
    bytes += struct.pack(short_endian, self.data['num_public_tagnames'])
    bytes += struct.pack(int_endian, self.data['public_tagnames_offset'])
    bytes += struct.pack(short_endian, self.data['pad'])
    return bytes


class AMXFunctionStub:
  def __init__(self, reader, address = 0, name = ""):
    self.data = {}
    if reader is None:
      #parse from string
      self.data['address'] = int(address)
      self.data['name'] = name
      self.data['instructions'] = []
    else:
      #parse from reader
      self.data['address'] = int.from_bytes(reader.read(4), byteorder=endian, signed=False)
      self.data['name'] = reader.read(20).decode().rstrip("\u0000")
      self.data['instructions'] = []

  def set_instructions(self, instructions):
    self.data['instructions'] = instructions.copy()

  def print_data(self):
    print("--------------- AMX Function Stub ---------------")
    print("address" + " : " + str(self.data['address']))
    print("name" + " : " + str(self.data['name']))

  def size(self):
    size = 24 #header bytes
    return size;
  
  def ins_size(self):
    size = 0 
    for ins in  self.data['instructions']:
      size += ins.size()
    return size

  def to_bytes(self):
    bytes = struct.pack(int_endian, self.data['address'])
    bytes += self.data['name'].encode("utf-8")
    #add additional bytes for function name limit of 20
    for i in range(20-len(self.data['name'])):
      bytes += int(0).to_bytes(1, endian)
    return bytes

class AMXInstruction:
  def __init__(self, code, index):
    self.data = {}
    if index == -1:
      #code is a input string
      code_string = code.split()
      code_len = len(code_string)
      if code_len < 3:
        sys.exit("Invalid line: " + code)
      argc = code_len - 4
      self.data['opcode'] = Labels[code_string[2].decode()].value
      self.data['opcode_name'] = code_string[2]
      self.data['args'] = []
      for i in range(argc):
        self.data['args'].append(int(code_string[4+i]))
      self.data['argcount'] = len(self.data['args'])
    else: 
      self.data['offset'] = index[0]
      #code is a bytes array
      self.data['opcode'] = int.from_bytes(code[index[0]:index[0]+op_len], byteorder=endian, signed=False)
      index[0] += op_len
      if self.data['opcode'] not in Labels._value2member_map_:
        print ("Invalid opcode: " + hex(self.data['opcode']) + " found at " + str(index[0]))
        return

      self.data['opcode_name'] = Labels(self.data['opcode']).name
      #get args
      self.data['argcount'] = label_enum_to_data[Labels(self.data['opcode'])].argcount
      self.data['args'] = []

      #if argcount = -1 then it has arbitrary amount of arge
      if self.data['argcount'] == -1:
        #read next byte for argcount
        self.data['args'].append(int.from_bytes(code[index[0]:index[0]+arg_len], byteorder=endian, signed=False))
        index[0] += arg_len
        for i in range(2*self.data['args'][0]):
          self.data['args'].append(int.from_bytes(code[index[0]:index[0]+arg_len], byteorder=endian, signed=False))
          index[0] += arg_len
        #1 more i guess???
        self.data['args'].append(int.from_bytes(code[index[0]:index[0]+arg_len], byteorder=endian, signed=False))
        index[0] += arg_len
        self.data['argcount'] = len(self.data['args'])
      else:
        for i in range(self.data['argcount']):
          self.data['args'].append(int.from_bytes(code[index[0]:index[0]+arg_len], byteorder=endian, signed=False))
          index[0] += arg_len
      
  def print_data(self):
    print("--------------- AMX Instruction ---------------")
    for item in self.data:
      print(item + " : " + str(self.data[item]))
  
  def to_string(self, relative_index, native_functions, data, arguments, last_function, pri_dict, last_push_c):
    out_string = str(relative_index[0]) + "," + str(self.data['offset']) + " : "
    relative_index[0] += op_len
    if self.data['opcode'] not in Labels._value2member_map_:
      out_string += str(self.data['opcode'])
    else:
      out_string += self.data['opcode_name']
      if self.data['argcount']:
        out_string += " -- "
      for arg in self.data['args']:
        out_string += str(arg)
        out_string += " "
        relative_index[0] += op_len
      if self.data['opcode_name'] == "OP_SYSREQ_C":
        out_string += "    # "
        function = native_functions[self.data['args'][0]].data['name']
        function += "("
        #a value prepends function calls which says how many arguments it uses
        arg_count = math.floor(last_push_c[0]/4);
        #remove last_push_c since its not a real argument
        arguments.pop()
        count = 0
        for i in reversed(range(len(arguments) - arg_count, len(arguments))):
          count += 1
          if arguments:
            function += str(arguments[i])
            arguments.pop()
          else:
            #Somehow we have fewer arguments than we need
            function += ("UNKNOWN")
          if count < arg_count:
            function += ','
        function += ")"
        last_function[0] = function
        out_string += function
        out_string += ";"
      elif self.data['opcode_name'] == "OP_PUSH_C":
        value = int_array_to_string(data[self.data['args'][0]:])
        last_push_c[0] = self.data['args'][0]
        if value:
          out_string += "    # "
          var_string = '"'
          var_string += value
          var_string += "\" or "
          var_string += str(self.data['args'][0])
          out_string += var_string
          arguments.append(var_string)
        else:
          arguments.append(self.data['args'][0])
      elif self.data['opcode_name'] == "OP_PUSH":
        value = "pri[" + str(self.data['args'][0]) + "]"
        out_string += "    # "
        out_string += value
        if self.data['args'][0] in pri_dict.keys():
          function = " - result of "
          function += pri_dict[self.data['args'][0]]
          out_string += function
          arguments.append(value + " /*" + pri_dict[self.data['args'][0]] + "*/")
        else:
          arguments.append(value)
      elif self.data['opcode_name'] == "OP_PUSH_PRI":
        value = last_function[0]
        out_string += "    # result of "
        out_string += value
        arguments.append(value)
      elif self.data['opcode_name'] == "OP_STOR_PRI":
        value = self.data['args'][0]
        out_string += "    # stored at pri["
        out_string += str(value)
        out_string += "]"
        pri_dict[value] = last_function[0]
        
    out_string += "\n"
    return out_string

  def size(self):
    size = 4 #header bytes
    size += 4 * self.data['argcount']
    return size;
 
  def to_bytes(self):
    op_bytes = struct.pack(uint_endian, self.data['opcode'])
    ret_bytes = sma_functions.encode_bin(op_bytes, 1)
    arg_bytes = bytearray()
    for arg in self.data['args']:
      arg_bytes += struct.pack(uint_endian, arg)
    ret_bytes += sma_functions.encode_bin(arg_bytes, len(self.data['args']))
    return ret_bytes
    
