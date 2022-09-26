import argparse
import os

#lazily add modules local or not so this script can be called by other scripts
# really should repackage as a library or something
try:
  from .mst_lib.misc import BinaryIO
  from .mst_lib.mst import MST
except:
  from mst_lib.misc import BinaryIO
  from mst_lib.mst import MST


def extract(mst_path, out_path, ignore_existing, file_to_extract, disable_formatting):
  br = BinaryIO(open(mst_path, 'rb'))

  mst = MST()
  little_endian = mst.read(br, disable_formatting)

  try:
    os.makedirs(out_path, exist_ok=True)
  except OSError:
    raise Exception("Couldn't create output path.")

  for file in mst.files:
    #only extract file to extract if given
    if (file_to_extract and file_to_extract == file.name) or not file_to_extract:
      file_out_path = os.path.join(out_path, file.name)
      if not disable_formatting:
        file_out_path = file_out_path.replace('.tga', '.dds')

      if os.path.isfile(file_out_path) and ignore_existing:
        print('Skipping {0.name}'.format(file))
        continue

      print('Writing {0.name} ({0.length} bytes @ {0.location}) loader: {0.loader}'.format(file))
      out_handle = open(file_out_path, 'wb')
      file.loader.read(br)
      file.loader.save(out_handle)

  #return endian for parent functions
  return little_endian


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('mst', help="path to the Metal Arms .MST file")
  parser.add_argument('path', help="directory to put the extracted files in")
  parser.add_argument('--ignore-existing', dest='ignore_existing', action='store_true')
  parser.add_argument('-f', '--file', help="extract only specific file")
  parser.add_argument('-n', '--no-formatting', help="Do not do any post processing to extracted files", action='store_true')
  parser.set_defaults(ignore_existing=False)
  args = parser.parse_args()
  extract(args.mst, args.path, args.ignore_existing, args.file, args.no_formatting)
