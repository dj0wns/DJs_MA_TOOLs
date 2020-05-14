import zipfile
import shutil
import tempfile
import os
import argparse

import mst_extract, mst_insert, wld_extractor

def execute(mst, modfile):
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
    if f_to_open.endswith(".wld"):
      try:
        #First extract the wld file
        wld_tempdir = tempfile.mkdtemp()
        little_endian = mst_extract.extract(mst, wld_tempdir, False, f_to_open)
        #now insert shapes into the wld
        wld_file = os.path.join(wld_tempdir, f_to_open)
        wld_extractor.execute(not little_endian, False, False, True, False, wld_file, dirpath)
        #now insert wld back into the mst
        mst_insert.execute(not little_endian, mst, [wld_file])
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
  parser.add_argument("mst", help="A game MST you want to modify")
  parser.add_argument("modfile", help="a zipfile containing the mod you want to edit")
  args = parser.parse_args()

  execute(args.mst, args.modfile)

