import sys
import os
import shutil
import re
import glob
import struct
import math
import collections
import argparse
import csv
from lib import csv_classes


fpath=os.path.realpath(__file__)
py_path=os.path.dirname(fpath)
endian = "little"
pack_int = '<i'
INT_BYTES=4
STR_BYTES=20


def parseError(error_string, line, index):
  sys.exit("Invalid line in csv. Line: " + str(line) + " - Index: " + str(index) + " " + error_string)
  

def iterateRow(line, row, current_keystring, current_fields, csv_header):
  for i in range(len(row)):
    if i == 0:
      if not row[i]:
        #not a new keystring but continuation of the previous line
        if not current_keystring:
          parseError("Leading comma without a valid keystring.", line, i)
        #else just let the rest of the elements be added as fields
      elif row[i][0] == '#':
        #comment do nothing
        print("Skipping line: " + str(line) + " because it is commented out")
        return current_keystring, current_fields
      elif row[i] and row !="#":
        #add new keystring
        if not current_keystring:
          current_keystring = row[i]
        elif len(current_fields):
          csv_header.addTable(current_keystring, current_fields)
          current_keystring = row[i]
          current_fields = []
        else:
          parseError("Keystring: " + current_keystring + " does not have any fields.", line, i)
    else:
      if not row[i]:
        #skip
        None
      elif row[i][0] == '#':
        #comment, continue
        print("Skipping line: " + str(line) + " after cell: " + str(i) + " because it is commented out")
        return current_keystring, current_fields
      else:
        #add field to list
        current_fields.append(row[i])
  return current_keystring, current_fields

def execute(is_big_endian, print, input_csv, output_csv):
  if is_big_endian:
    #lazy but also set these in all sub classes
    csv_classes.endian='big'
    csv_classes.float_endian = '>f'
    csv_classes.int_endian = '>i'
    csv_classes.short_endian = '>h' 
  else:
    #lazy but also set these in all sub classes
    csv_classes.endian='little'
    csv_classes.float_endian = '<f'
    csv_classes.int_endian = '<i'
    csv_classes.short_endian = '<h'  

  input_reader = open(input_csv, newline='')
  csv_reader = csv.reader(input_reader, delimiter=',')
  
  csv_header = csv_classes.CSVHeader()

  current_keystring = ""
  current_fields = []
  line = 0;
  for row in csv_reader:
    current_keystring, current_fields = iterateRow(line, row, current_keystring, current_fields, csv_header)
    line+=1
  
  #add last fields if they exist
  if current_keystring:
    if len(current_fields):
      csv_header.addTable(current_keystring, current_fields)
    else:
      parseError("Keystring: " + current_keystring + " does not have any fields.", line, 0)

  #now convert header to bytes!
  #run twice to fix indices
  if print:
    csv_header.pretty_print()
  csv_header.to_bytes()
  
  input_reader.close()
  csv_writer = open(output_csv, "wb")
  csv_writer.write(csv_header.to_bytes())


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Rebuild a CSV file")
  endian = parser.add_mutually_exclusive_group()
  endian.add_argument("-g", "--gamecube", help="Use gamecube endian - small endian", action="store_true")
  endian.add_argument("-x", "--xbox", help="Use xbox endian - big endian [Default]", action="store_true")
  parser.add_argument("-p", "--print", help="Print the parsed csv", action="store_true")
  parser.add_argument("input", help="Input CSV file")
  parser.add_argument("output", type=str, help="Output file")
  args = parser.parse_args()
  #set endianess - xbox default
  execute(args.gamecube, args.print, args.input, args.output)
