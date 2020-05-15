import zipfile
import shutil
import tempfile
import os
import argparse
from distutils.util import strtobool

import mst_extract, mst_insert, wld_extractor

file_type_list =[
  ".ape",
  ".cam",
  ".csv",
  ".dds",
  ".fnt",
  ".fpr",
  ".gt",
  ".mtx",
  ".new",
  ".rdg",
  ".rdx",
  ".sfb",
  ".sfb",
  ".sma",
  ".wvb"]

def execute(mst, modfile, newMST):
  try:
    # get temporary folder to extract zip to
    dirpath = tempfile.mkdtemp()
    # first find a temporary file to write the wld to
    with zipfile.ZipFile(modfile, 'r') as zip_ref:
      for member in zip_ref.namelist():
        filename = os.path.basename(member)
        if not filename:
          continue
        source = zip_ref.open(member)
        target = open(os.path.join(dirpath, filename), 'wb')
        with source, target:
          shutil.copyfileobj(source, target)
    config_path = os.path.join(dirpath, "config.txt")
    if not os.path.isfile(config_path):
      print ("Tell the asshole who made this mod to includ a config.txt in the root directory.")
      return
    with open(config_path, 'r') as file:
      f_to_open = file.readline().strip()
    files_to_insert = []
    try:
      wld_tempdir = tempfile.mkdtemp()
      if f_to_open.endswith(".wld"):
        #First extract the wld file
        little_endian = mst_extract.extract(mst, wld_tempdir, False, f_to_open)
        #now insert shapes into the wld
        wld_file = os.path.join(wld_tempdir, f_to_open)
        wld_extractor.execute(not little_endian, False, False, True, False, wld_file, dirpath)
        #prompt user if this is ok
        while True:
          try:
            value = strtobool(input("By default this mod replaces " + f_to_open + ". Would you like to replace a different .wld instead? "))
          except ValueError:
            continue
          if not value:
            break
          new_wld = input("Which .wld would you like to replace? ")
          os.rename(wld_file, os.path.join(wld_tempdir, new_wld))
          wld_file = os.path.join(wld_tempdir, new_wld)
          break
        files_to_insert.append(wld_file)
      else:
        little_endian = mst_extract.extract(mst, wld_tempdir, False, "NO_FILE")

      #now get other non-json files in the mst and insert them
      for f in os.listdir(dirpath):
        name, extension = os.path.splitext(f)
        if extension in file_type_list:
          files_to_insert.append(os.path.join(dirpath,f))
      #let the user know what is being inserted
      print("This mod will replace the following files: ")
      for f in files_to_insert:
        filename = os.path.basename(f)
        print(filename)
      #prompt user if this is ok
      while True:
        try:
          value = strtobool(input("Continue? "))
        except ValueError:
          continue
        if not value:
          return
        break

      #now insert wld back into the mst
      if newMST:
        mst_insert.execute(not little_endian, mst, files_to_insert, ".new")
      else:
        mst_insert.execute(not little_endian, mst, files_to_insert, "")
    except Exception as e:
      print(e)
    finally:
      #make sure to clean up after ourselves
      shutil.rmtree(wld_tempdir)


  except Exception as e:
    print(e)
  finally:
    #make sure to clean up after ourselves
    shutil.rmtree(dirpath)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Extract or rebuild a wld file")
  parser.add_argument("-n", "--newMST", help="Output a new mst, by default it overwrites the original mst", action='store_true')
  parser.add_argument("mst", help="A game MST you want to modify")
  parser.add_argument("modfile", help="a zipfile containing the mod you want to edit")
  args = parser.parse_args()

  execute(args.mst, args.modfile, args.newMST)

