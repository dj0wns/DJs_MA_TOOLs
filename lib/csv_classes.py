import struct
import os
import sys
import json

from . import ma_util

#globals because i dont want to rewrite this - make sure to set them to the correct value - xbox default
endian='little'
float_endian = '<f'
int_endian = '<i'
short_endian = '<h'

csv_datatype = [
  "STRING",
  "FLOAT",
  "WIDESTRING",
  "COUNT"]

csv_datavalue = {
  "STRING" : 0,
  "FLOAT" : 1,
  "WIDESTRING" : 2,
  "COUNT" : 3}

class CSVHeader:
  #dictionary where key is name and value is value
  def __init__(self):
    self.tables = []
    self.flags = 0
  
  def addTable(self, keystring, fields):
    self.tables.append(CSVTable(keystring, fields, len(self.tables)))
  
  def pretty_print(self):
    #print csv
    print("--------------- Game Data CSV ---------------")
    for item in self.tables:
      row = str(item.data['keystring'])
      row +=  " - " + str(item.data['keystring_length'])
      row += ","
      for field in item.fields:
        row += str(field.data_string())
        row += ","
      row = row[:-1] #remove trailing comma
      print(row)

  def size(self):
    size = 16 #header bytes
    for table in self.tables:
      size += table.size()
    return size;

  def to_bytes(self):
    #returns a byte array that can be lopped in with the other csv's
    byteheader = struct.pack(int_endian, self.size())
    byteheader += struct.pack(int_endian, len(self.tables))
    byteheader += struct.pack(int_endian, 16) #size of the header, i think its always 16
    byteheader += struct.pack(int_endian, self.flags)
    offset = (len(self.tables) * 16) + 16 #keystring headers are 16 bytes
    table_offset = offset #used to find the offset of the data part within a table's fields
    self.pointer_to_tables = len(byteheader)
    for table in self.tables:
      newheader = table.header_to_bytes(offset)
      byteheader += newheader
      offset += table.size() - 16 #-16 because the current header's count is already counted i guess #TODO check this
    #after headers you start pasting in values - not sure where the strings are kept yet
    for table in self.tables:
      #add keystrings
      table.data['keystring_pointer'] = len(byteheader)
      newbytes, size = table.keystring_to_bytes()
      byteheader += newbytes
      table_offset += size + len(table.fields) * 12 #data(strings) come after the keystring + fields
      table.data['field_offset'] = len(byteheader)
      #add fields
      for field in table.fields:
        new_bytes = field.to_bytes(table_offset)
        if field.data['string_length'] > 0:
          if field.data['data_type'] == "STRING":
            table_offset += field.data['string_length'] + 1
          elif field.data['data_type'] == "WIDESTRING":
            #round beginning
            table_offset = ma_util.roundup_2(table_offset) 
            table_offset += 2*(field.data['string_length'] + 1)
        byteheader += new_bytes
      #add field strings
      for field in table.fields:
        if field.data['data_type'] == "STRING":
          new_bytes = bytearray(field.data['string'].encode("utf-8"))
          new_bytes.append(0x0)
          byteheader += new_bytes
        elif field.data['data_type'] == "WIDESTRING":
          #wide string appears to conform to 2 byte boundaries
          toadd = ma_util.roundup_2(len(byteheader)) - len(byteheader)
          for i in range(toadd):
            byteheader += b'\x00'
          if endian == "little":
            new_bytes = bytearray(field.data['widestring'].encode("utf-16-le"))
          else:  
            new_bytes = bytearray(field.data['widestring'].encode("utf-16-be"))
          new_bytes.append(0x0)
          byteheader += new_bytes   
          #wide string appears to conform to 2 byte boundaries, so pad beginning and end
          toadd = ma_util.roundup_2(len(byteheader)) - len(byteheader)
          for i in range(toadd):
            byteheader += b'\x00'
    return byteheader

class CSVTable:
  def __init__(self, keystring, fields, table_count):
    self.data = {}
    self.data['keystring'] = keystring
    self.data['keystring_length'] = len(keystring)
    self.data['num_fields'] = len(fields)
    self.data['keystring_pointer'] = 0
    self.data['field_offset'] = 0
    self.data['table_index'] = table_count
    self.fields = []
    for field in fields:
      self.fields.append(CSVField(keystring, field))
  
  def print_data(self):
    print("--------------- Game Data Table ---------------")
    for item in self.data:
      print(item + " : " + str(self.data[item]))
    for item in self.fields:
      item.print_data()
  
  def size(self):
    size = 16 #header
    size += ma_util.roundup_4(self.data['keystring_pointer'] + self.data['keystring_length']+1) - (self.data['keystring_pointer']); 
    size += self.child_size()
    return size;
  
  def child_size(self):
    size = 0
    for field in self.fields:
      size += field.size()
    return size;
    

  def header_to_bytes(self, keystring_pointer):
    byteheader = struct.pack(int_endian, keystring_pointer) #parent has to figure out where it goes because its managing the rebuild
    byteheader += struct.pack(int_endian, self.data['keystring_length'])
    byteheader += struct.pack(short_endian, self.data['num_fields'])
    byteheader += struct.pack(short_endian, self.data['table_index'])
    byteheader += struct.pack(int_endian, self.data['field_offset'])
    return byteheader

  def keystring_to_bytes(self):
    keystring = bytearray(self.data['keystring'].encode("utf-8"))
    #add additional padding to the string
    size = ma_util.roundup_4(self.data['keystring_pointer'] + self.data['keystring_length'] + 1) - (self.data['keystring_pointer']); 
    to_add = size - len(keystring)
    for i in range(to_add):
      keystring.append(0x0)
     
    byteheader = keystring
    return byteheader, size
    

class CSVField:
  def __init__(self, keystring, field):
    self.data = {}
    if ma_util.isfloat(field):
      self.data['data_type'] = "FLOAT"
      self.data['float'] = float(field)
      self.data['string_length'] = 0
    elif keystring.lower() == "missiontext":
      self.data['data_type'] = "WIDESTRING"
      self.data['widestring'] = field
      self.data['string_length'] = len(field)
    else:
      self.data['data_type'] = "STRING"
      self.data['string'] = field
      self.data['string_length'] = len(field)


  def data_string(self):
    if self.data['data_type'] == "STRING":
      return self.data['string']
    elif self.data['data_type'] == "WIDESTRING":
      return self.data['widestring']
    else:
      return self.data['float']
  
  def size(self):
    size = 12 #header size
    #if data is a string, dont forget to add 4 bytes for the offset
    if self.data['data_type'] == "STRING":
      size += 1 
      size += self.data['string_length'] #this string does not appear to be rounded up
    elif self.data['data_type'] == "WIDESTRING":
      size += 2*(self.data['string_length'] + 1) #wide strings are twice as wide
    return size;
  
  def to_bytes(self, offset):
    byteheader = struct.pack(int_endian, csv_datavalue[self.data['data_type']])
    #data - either a pointer or a float
    if self.data['data_type'] == "STRING" or self.data['data_type'] == "WIDESTRING":
      byteheader += struct.pack(int_endian, offset) #parent has to figure out where it goes because its managing the rebuild
    else:
      byteheader += struct.pack(float_endian, self.data['float']) #no string, no offset
    #string length
    if self.data['data_type'] == "STRING" or self.data['data_type'] == "WIDESTRING":
      byteheader += struct.pack(int_endian, self.data['string_length'])
    else: 
      byteheader += struct.pack(int_endian, 0) #no string, no offset
    return byteheader
