import sys
import os
import shutil


fpath=os.path.realpath(__file__)
py_path=os.path.dirname(fpath)

class Header:
  #Dictionary where key is name and value is value
  def __init__(self, writer):
    self.data = self.header_parse(writer)

  def header_parse(self, writer): 
    header = {}
    header['file_size'] = int.from_bytes(writer.read(4), byteorder='little', signed=False)
    header['item_count'] = int.from_bytes(writer.read(4), byteorder='little', signed=False) #maybe meshes or something
    header['header_size'] = int.from_bytes(writer.read(4), byteorder='little', signed=False)
    header['start_of_first_part'] = int.from_bytes(writer.read(4), byteorder='little', signed=False)
    header['size_of_first_part'] = int.from_bytes(writer.read(4), byteorder='little', signed=False)
    header['start_of_second_part'] = int.from_bytes(writer.read(4), byteorder='little', signed=False)
    header['size_of_second_part'] = int.from_bytes(writer.read(4), byteorder='little', signed=False)
    header['start_of_third_part'] = int.from_bytes(writer.read(4), byteorder='little', signed=False)
    header['size_of_third_part'] = int.from_bytes(writer.read(4), byteorder='little', signed=False)
    header['start_of_fourth_part'] = int.from_bytes(writer.read(4), byteorder='little', signed=False)
    header['size_of_fourth_part'] = int.from_bytes(writer.read(4), byteorder='little', signed=False)
    return header

  def print_header(self):
    print("--------------- Header ---------------")
    for item in self.data:
      print(item + " : " + str(self.data[item]))

  def write_body_files(self,writer,filename,end_of_ape):
    folder = os.path.join(py_path, filename)
    if os.path.isdir(folder) : 
      #Placeholder to do nothing, should delete all files
      None
    else:
      os.mkdir(folder)
    
    #Write Header
    writer.seek(0, os.SEEK_SET)
    file_bytes = writer.read(self.data['start_of_first_part'])
    out_file = os.path.join(folder,"Header")
    f = open(out_file, 'wb')
    f.write(file_bytes)
    f.close()
   
    #write First_Part_Suffix
    writer.seek(end_of_apes, os.SEEK_SET)
    file_bytes = writer.read(self.data['start_of_second_part'] - end_of_apes)
    out_file = os.path.join(folder,"First_Part_Suffix")
    f = open(out_file, 'wb')
    f.write(file_bytes)
    f.close()


    #write part 2
    writer.seek(self.data['start_of_second_part'], os.SEEK_SET)
    file_bytes = writer.read(self.data['size_of_second_part'])
    out_file = os.path.join(folder,"Second_Part")
    f = open(out_file, 'wb')
    f.write(file_bytes)
    f.close()
    
    #write part 3
    writer.seek(self.data['start_of_third_part'], os.SEEK_SET)
    file_bytes = writer.read(self.data['size_of_third_part'])
    out_file = os.path.join(folder,"Third_Part")
    f = open(out_file, 'wb')
    f.write(file_bytes)
    f.close()
    
    #write part 4
    writer.seek(self.data['start_of_fourth_part'], os.SEEK_SET)
    file_bytes = writer.read(self.data['size_of_fourth_part'])
    out_file = os.path.join(folder,"Fourth_Part")
    f = open(out_file, 'wb')
    f.write(file_bytes)
    f.close()
    
    
class Items:
  #Dictionary where key is offset and value is size
  def __init__(self, writer, header):
    self.data = self.items_parse(writer, header)

  def items_parse(self, writer, header):
    item_count = header.data['item_count']
    location_list = []
    size_list = []

    for i in range(item_count):
      location_list.append(int.from_bytes(writer.read(4), byteorder='little', signed=False))
    for i in range(item_count):
      size_list.append(int.from_bytes(writer.read(4), byteorder='little', signed=False))

    #to dictionary
    dictionary = dict(zip(location_list, size_list))
    return dictionary
  
  def print_items(self):
    print("--------------- Items ---------------")
    for item in self.data:
      print("Item Offset: " + str(item) + " - " +  hex(item) + ", Size: " + str(self.data[item]) + ", End: " + str(item + self.data[item]))

  def write_items(self,writer,filename):
    #make dir if doesnt exist
    #if does exist, remove all files
    folder = os.path.join(py_path, filename)
    if os.path.isdir(folder) : 
      #Placeholder to do nothing, should delete all files
      None
    else:
      os.mkdir(folder)
    
    #write (APE???) files
    i = 0
    for item in self.data:
      writer.seek(item, os.SEEK_SET)
      file_bytes = writer.read(self.data[item])
      out_file = os.path.join(folder,str(i).zfill(3))
      f = open(out_file, 'wb')
      f.write(file_bytes)
      f.close()
      #increment counter
      i = i + 1
   
    return writer.tell()

class Item:
  def __init__(self, writer, offset, length):
    self.data = self.item_parse(writer, offset, length)

  def item_parse(self, writer, offset, length):
    writer.seek(offset, os.SEEK_SET)
    data = {}
    data['name'] = writer.read(16).decode()

    return data


  def print_item(self):
    print("--------------- Item ---------------")
    for item in self.data:
      print(str(item) + ":" + str(self.data[item]))

if __name__ == '__main__':
  if len(sys.argv) < 2 : 
    print("Requires a file as an argument")
    sys.exit()

  path = sys.argv[1]
  writer = open(path, "rb")

  #extract name for creating a working folder
  basename = os.path.basename(path)
  filename, file_extension = os.path.splitext(basename)

  header = Header(writer)
  header.print_header()
  
  items = Items(writer, header)
  items.print_items()

  end_of_apes = items.write_items(writer,filename)
  header.write_body_files(writer,filename,end_of_apes)

  kv = next(iter(items.data.items()))
  
  item = Item(writer, kv[0], kv[1])
  item.print_item()
