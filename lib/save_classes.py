import struct
import os
import sys
import json
import itertools
import zlib
from bidict import bidict

from . import ma_util

#globals because i dont want to rewrite this - make sure to set them to the correct value - xbox default
endian='little'
float_endian = '<f'
int_endian = '<I'
short_endian = '<H'
char_endian = 'B'

quick_select_names = ["Up", "Down", "Left", "Right"]

item_crc_bidict = bidict({"Null": 0})
for item in ma_util.item_tag_names:
  item_padded = item + '\0' * (64-len(item))
  name_bytes = item_padded.encode('ascii')
  crc = zlib.crc32(name_bytes)
  item_crc_bidict[item] = crc

class ProfileData:
  def __init__(self):
    self.data = {}
    #build item tag table
      

  def parse_bytes(self, reader):
    self.data = {}
    self.data['offset'] = reader.tell()
    header = ProfileHeader()
    header.parse_bytes(reader)
    self.data['header'] = header
    self.data['flags'] = int.from_bytes(reader.read(4), byteorder=endian, signed=False)
    self.data['difficulty'] = int.from_bytes(reader.read(1), byteorder=endian, signed=False)
    self.data['current_level'] = int.from_bytes(reader.read(1), byteorder=endian, signed=False)
    self.data['controller_config_index'] = int.from_bytes(reader.read(1), byteorder=endian, signed=False)
    self.data['color_index'] = int.from_bytes(reader.read(1), byteorder=endian, signed=False)
    self.data['mp_rules_count'] = int.from_bytes(reader.read(1), byteorder=endian, signed=False)
    self.data['total_secret_chips_gathered'] = int.from_bytes(reader.read(1), byteorder=endian, signed=False)
    self.data['mp_levels_unlocked'] = int.from_bytes(reader.read(1), byteorder=endian, signed=False)
    self.data['padding'] = int.from_bytes(reader.read(1), byteorder=endian, signed=False)
    self.data['vibration_intensity'] = struct.unpack(float_endian, reader.read(4))[0]
    self.data['look_sensitivity'] = struct.unpack(float_endian, reader.read(4))[0]
    self.data['sound_level'] = struct.unpack(float_endian, reader.read(4))[0]
    self.data['music_level'] = struct.unpack(float_endian, reader.read(4))[0]
    sp_qselect = QuickSelectObject()
    sp_qselect.parse_bytes(reader)
    self.data['sp_quick_select'] = sp_qselect
    mp_qselect = QuickSelectObject()
    mp_qselect.parse_bytes(reader)
    self.data['mp_quick_select'] = mp_qselect
    self.data['level_progress'] = []
    for i in range(42): #sp levels
      level_progress = LevelProgress()
      level_progress.level_name = ma_util.level_names[i]
      level_progress.parse_bytes(reader)
      self.data['level_progress'].append(level_progress)
    self.data['mp_rules'] = []
    for i in range(16): #mp level rules
      mp_rules = MPRules()
      mp_rules.parse_bytes(reader)
      self.data['mp_rules'].append(mp_rules)

      

  def print_data(self):
    print("--------------- Profile Data ---------------")
    self.data['header'].print_data()
    for item in self.data:
      print(item + " : " + str(self.data[item]))
    self.data['sp_quick_select'].print_data()
    self.data['mp_quick_select'].print_data()
    for item in self.data['level_progress']:
      item.print_data()
    for item in self.data['mp_rules']:
      item.print_data()
   
  def to_bytes(self):
    bytes = self.data['header'].to_bytes()
    bytes += struct.pack(int_endian, self.data['flags'])
    bytes += struct.pack(char_endian, self.data['difficulty'])
    bytes += struct.pack(char_endian, self.data['current_level'])
    bytes += struct.pack(char_endian, self.data['controller_config_index'])
    bytes += struct.pack(char_endian, self.data['color_index'])
    bytes += struct.pack(char_endian, self.data['mp_rules_count'])
    bytes += struct.pack(char_endian, self.data['total_secret_chips_gathered'])
    bytes += struct.pack(char_endian, self.data['mp_levels_unlocked'])
    bytes += struct.pack(char_endian, self.data['padding'])
    bytes += struct.pack(float_endian, self.data['vibration_intensity'])
    bytes += struct.pack(float_endian, self.data['look_sensitivity'])
    bytes += struct.pack(float_endian, self.data['sound_level'])
    bytes += struct.pack(float_endian, self.data['music_level'])
    bytes += self.data['sp_quick_select'].to_bytes()
    bytes += self.data['mp_quick_select'].to_bytes()
    for item in self.data['level_progress']:
      bytes += item.to_bytes()
    for item in self.data['mp_rules']:
      bytes += item.to_bytes()
    return bytes
  
  def size(self):
    size = 28 #bytes
    size += self.data['header'].size()
    size += self.data['sp_quick_select'].size()
    size += self.data['mp_quick_select'].size()
    for item in self.data['level_progress']:
      size += item.size()
    for item in self.data['mp_rules']:
      size += item.size()
    return size

class ProfileHeader:
  def __init__(self):
    self.data = {}

  def parse_bytes(self, reader):
    self.data = {}
    self.data['offset'] = reader.tell()
    self.data['signature'] = int.from_bytes(reader.read(4), byteorder=endian, signed=False)
    self.data['file_version'] = int.from_bytes(reader.read(4), byteorder=endian, signed=False)
    self.data['profile_crc'] = int.from_bytes(reader.read(4), byteorder=endian, signed=False)
    self.data['profile_bytes'] = int.from_bytes(reader.read(4), byteorder=endian, signed=False)

  def print_data(self):
    print("--------------- Profile Header ---------------")
    for item in self.data:
      print(item + " : " + str(self.data[item]))
   
  def to_bytes(self):
    bytes = struct.pack(int_endian, self.data['signature'])
    bytes += struct.pack(int_endian, self.data['file_version'])
    bytes += struct.pack(int_endian, self.data['profile_crc'])
    bytes += struct.pack(int_endian, self.data['profile_bytes'])
    return bytes
  
  def size(self):
    size = 16 #bytes
    return size

class LevelProgress:
  def __init__(self):
    self.level_name = ""
    self.data = {}

  def parse_bytes(self, reader):
    self.data = {}
    self.data['offset'] = reader.tell()
    self.data['completion_time'] = struct.unpack(float_endian, reader.read(4))[0]
    self.data['secret_chips'] = int.from_bytes(reader.read(2), byteorder=endian, signed=False)
    self.data['bonus_secret_chip_earned'] = int.from_bytes(reader.read(2), byteorder=endian, signed=False)
    self.data['washers_collected'] = int.from_bytes(reader.read(2), byteorder=endian, signed=False)
    self.data['enemies_killed'] = int.from_bytes(reader.read(2), byteorder=endian, signed=False)
    inventory = Inventory()
    inventory.parse_bytes(reader)
    self.data['inventory'] = inventory

  def print_data(self):
    print("--------------- Level Progress ---------------")
    for item in self.data:
      print(item + " : " + str(self.data[item]))
    self.data["inventory"].print_data()
   
  def to_bytes(self):
    bytes = struct.pack(float_endian, self.data['completion_time'])
    bytes += struct.pack(short_endian, self.data['secret_chips'])
    bytes += struct.pack(short_endian, self.data['bonus_secret_chip_earned'])
    bytes += struct.pack(short_endian, self.data['washers_collected'])
    bytes += struct.pack(short_endian, self.data['enemies_killed'])
    bytes += self.data["inventory"].to_bytes()
    return bytes
  
  def size(self):
    size = 12 #bytes
    size += self.data["inventory"].size()
    return size

class MPRules:
  def __init__(self):
    self.data = {}

  def parse_bytes(self, reader):
    self.data = {}
    self.data['offset'] = reader.tell()
    self.data['flags'] = int.from_bytes(reader.read(2), byteorder=endian, signed=False)
    if endian == 'little':
      self.data['game_name'] = reader.read(34).decode('utf-16-le') #remove trailing zeroes
    else:
      self.data['game_name'] = reader.read(34).decode('utf-16-be') #remove trailing zeroes
    self.data['game_type'] = int.from_bytes(reader.read(1), byteorder=endian, signed=False)
    self.data['dm_kills_per_round'] = int.from_bytes(reader.read(1), byteorder=endian, signed=False)
    self.data['time_limit'] = int.from_bytes(reader.read(1), byteorder=endian, signed=False)
    self.data['limit_primary_weapon'] = int.from_bytes(reader.read(1), byteorder=endian, signed=False)
    self.data['limit_secondary_weapon'] = int.from_bytes(reader.read(1), byteorder=endian, signed=False)
    self.data['limit_vehicles'] = int.from_bytes(reader.read(1), byteorder=endian, signed=False)
    self.data['time_between_hill_swaps'] = int.from_bytes(reader.read(1), byteorder=endian, signed=False)
    self.data['padding'] = int.from_bytes(reader.read(2), byteorder=endian, signed=False)


  def print_data(self):
    print("--------------- MP Rules ---------------")
    for item in self.data:
      print(item + " : " + str(self.data[item]))
   
  def to_bytes(self):
    bytes = struct.pack(short_endian, self.data['flags'])
    if endian == 'little':
      bytes += bytearray(self.data['game_name'].encode("utf-16-le"))
    else:
      bytes += bytearray(self.data['game_name'].encode("utf-16-be"))
    bytes += struct.pack(char_endian, self.data['game_type'])
    bytes += struct.pack(char_endian, self.data['dm_kills_per_round'])
    bytes += struct.pack(char_endian, self.data['time_limit'])
    bytes += struct.pack(char_endian, self.data['limit_primary_weapon'])
    bytes += struct.pack(char_endian, self.data['limit_secondary_weapon'])
    bytes += struct.pack(char_endian, self.data['limit_vehicles'])
    bytes += struct.pack(char_endian, self.data['time_between_hill_swaps'])
    bytes += struct.pack(short_endian, self.data['padding'])
    return bytes
  
  def size(self):
    size = 45 #bytes
    return size

class QuickSelect:
  def __init__(self):
    self.direction = ""
    self.data = {}

  def parse_bytes(self, reader):
    self.data = {}
    self.data['offset'] = reader.tell()
    self.data['primary'] = int.from_bytes(reader.read(4), byteorder=endian, signed=False)
    self.data['secondary'] = int.from_bytes(reader.read(4), byteorder=endian, signed=False)

  def print_data(self):
    print("--------------- QuickSelect ---------------")
    for item in self.data:
      print(item + " : " + str(self.data[item]))
   
  def to_bytes(self):
    bytes = struct.pack(int_endian, self.data['primary'])
    bytes += struct.pack(int_endian, self.data['secondary'])
    return bytes
  
  def size(self):
    size = 8 #bytes
    return size

class QuickSelectObject:
  def __init__(self):
    self.data = {}

  def parse_bytes(self, reader):
    self.data = {}
    self.data['offset'] = reader.tell()
    self.data['num_axes'] = int.from_bytes(reader.read(4), byteorder=endian, signed=False)
    self.data['quick_selects'] = []
    for i in range(4):
      q_select = QuickSelect()
      q_select.parse_bytes(reader)
      q_select.direction = quick_select_names[i]
      self.data['quick_selects'].append(q_select)

  def print_data(self):
    print("--------------- QuickSelectObject ---------------")
    print('offset' + " : " + str(self.data['offset']))
    print('num_axes' + " : " + str(self.data['num_axes']))
    for item in self.data['quick_selects']:
      item.print_data()
   
  def to_bytes(self):
    bytes = struct.pack(int_endian, self.data['num_axes'])
    for item in self.data['quick_selects']:
      bytes += item.to_bytes()
    return bytes

    bytes += struct.pack(int_endian, self.data['secondary'])
  
  def size(self):
    size = 4 #bytes
    for item in self.data['quick_selects']:
      size += item.size()
    return size

class Inventory:
  def __init__(self):
    self.data = {}

  def parse_bytes(self, reader):
    self.data = {}
    self.data['offset'] = reader.tell()
    self.data['num_primaries'] = int.from_bytes(reader.read(1), byteorder=endian, signed=True)
    self.data['num_secondaries'] = int.from_bytes(reader.read(1), byteorder=endian, signed=True)
    self.data['num_items'] = int.from_bytes(reader.read(1), byteorder=endian, signed=False)
    self.data['num_batteries'] = int.from_bytes(reader.read(1), byteorder=endian, signed=False)
    self.data['primary_weapons'] = []
    for i in range(16):
      inv_item = InventoryItem()
      inv_item.parse_bytes(reader)
      self.data['primary_weapons'].append(inv_item)
    self.data['secondary_weapons'] = []
    for i in range(16):
      inv_item = InventoryItem()
      inv_item.parse_bytes(reader)
      self.data['secondary_weapons'].append(inv_item)
    self.data['items'] = []
    for i in range(16):
      inv_item = InventoryItem()
      inv_item.parse_bytes(reader)
      self.data['items'].append(inv_item)
    self.data['euk_flags'] = []
    for i in range(10):
      self.data['euk_flags'].append(int.from_bytes(reader.read(2), byteorder=endian, signed=False))
    self.data['current_primary_weapon'] = int.from_bytes(reader.read(1), byteorder=endian, signed=False)
    self.data['current_secondary_weapon'] = int.from_bytes(reader.read(1), byteorder=endian, signed=False)
    self.data['saved_primary_weapon'] = int.from_bytes(reader.read(1), byteorder=endian, signed=False)
    self.data['saved_secondary_weapon'] = int.from_bytes(reader.read(1), byteorder=endian, signed=False)

  def print_data(self):
    print("--------------- Inventory Item ---------------")
    for item in self.data:
      print(item + " : " + str(self.data[item]))
   
  def to_bytes(self):
    bytes = struct.pack(char_endian, self.data['num_primaries'])
    bytes += struct.pack(char_endian, self.data['num_secondaries'])
    bytes += struct.pack(char_endian, self.data['num_items'])
    bytes += struct.pack(char_endian, self.data['num_batteries'])
    for item in self.data['primary_weapons']:
      bytes += item.to_bytes()
    for item in self.data['secondary_weapons']:
      bytes += item.to_bytes()
    for item in self.data['items']:
      bytes += item.to_bytes()
    for item in self.data['euk_flags']:
      bytes += struct.pack(short_endian, item)
    bytes += struct.pack(char_endian, self.data['current_primary_weapon'])
    bytes += struct.pack(char_endian, self.data['current_secondary_weapon'])
    bytes += struct.pack(char_endian, self.data['saved_primary_weapon'])
    bytes += struct.pack(char_endian, self.data['saved_secondary_weapon'])
    return bytes
  
  def size(self):
    size = 8 #bytes
    for item in self.data['primary_weapons']:
      size += item.size()
    for item in self.data['secondary_weapons']:
      size += item.size()
    for item in self.data['items']:
      size += item.size()
    for item in self.data['euk_flags']:
      size += 2
    return size

class InventoryItem:
  def __init__(self):
    self.data = {}

  def parse_bytes(self, reader):
    self.data = {}
    self.data['offset'] = reader.tell()
    self.data['item_name'] = item_crc_bidict.inverse[int.from_bytes(reader.read(4), byteorder=endian, signed=False)]
    self.data['upgrade_level'] = int.from_bytes(reader.read(2), byteorder=endian, signed=False)
    self.data['clip_ammo'] = int.from_bytes(reader.read(2), byteorder=endian, signed=False)
    self.data['reserve_ammo'] = int.from_bytes(reader.read(2), byteorder=endian, signed=False)
    self.data['display_type_1'] = int.from_bytes(reader.read(1), byteorder=endian, signed=False)
    self.data['display_type_2'] = int.from_bytes(reader.read(1), byteorder=endian, signed=False)

  def print_data(self):
    print("--------------- Inventory Item ---------------")
    for item in self.data:
      print(item + " : " + str(self.data[item]))
   
  def to_bytes(self):
    bytes = struct.pack(int_endian, item_crc_bidict[self.data['item_name']])
    bytes += struct.pack(short_endian, self.data['upgrade_level'])
    bytes += struct.pack(short_endian, self.data['clip_ammo'])
    bytes += struct.pack(short_endian, self.data['reserve_ammo'])
    bytes += struct.pack(char_endian, self.data['display_type_1'])
    bytes += struct.pack(char_endian, self.data['display_type_2'])
    return bytes
  
  def size(self):
    size = 12 #bytes
    return size
