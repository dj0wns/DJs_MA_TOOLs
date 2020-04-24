import ctypes
import os
dirname = os.path.dirname(__file__)
small_lib_name = os.path.join(dirname, 'libsmall.so')

_small = ctypes.CDLL(small_lib_name)


def expand(code, codesize, memsize):
  global _small
  if len(code) < memsize:
    #add padding
    for i in range (memsize - codesize):
      code.append(0)
  print(len(code))
  print(str(codesize) + "    " + str(memsize))
  mutable_string = ctypes.create_string_buffer(bytes(code))
  _small.expand(mutable_string, codesize, memsize)
  print(mutable_string)
  return mutable_string

def encode_bin(code_buffer, num):
  global _small
  bufsize = 200
  ret_buffer = bytearray()
  for i in range (bufsize):
    ret_buffer.append(0)
  
  mutable_string = ctypes.create_string_buffer(bytes(ret_buffer))
  
  size = _small.return_encoded(mutable_string, bytes(code_buffer), num)
  return mutable_string[:size]


